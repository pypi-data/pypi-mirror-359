#!/usr/bin/env python3
from abc import ABC, abstractmethod
import numpy as np
import math
import scipy.stats as stats 
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from sympy import symbols
from roboticstoolbox import ETS,ET
import time
import json
import socket
import zlib
import struct
import select
import threading
import logging
from typing import Dict, Any, Optional, List, Union

# Ctrl + K，然后 Ctrl + 0
np.set_printoptions(precision=6, suppress=True)  # suppress=True 去掉科学计数法

# 更新日志
# 2025.7.2 15:43更新psa_dh_calibrations_ets
class RobotDHCalibration(ABC):
    """DH参数标定类"""
    #ETS模式
    def rotz(self,theta):
        """
        说明：用于DH标定的(ETS模式)->绕 Z 轴旋转的 4x4 齐次变换矩阵(弧度)
        """
        c, s = np.cos(theta), np.sin(theta)
        return np.array([
            [c, -s, 0, 0],
            [s,  c, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1]
        ])
    def rotx(self,alpha):
        """
        说明：用于DH标定的(ETS模式)->绕 X 轴旋转的 4x4 齐次变换矩阵(弧度)
        """
        c, s = np.cos(alpha), np.sin(alpha)
        return np.array([
            [1, 0,  0, 0],
            [0, c, -s, 0],
            [0, s,  c, 0],
            [0, 0,  0, 1]
        ])
    def roty(self,beta):
        """
        说明：用于DH标定的(ETS模式)->绕 Y 轴旋转的 4x4 齐次变换矩阵(弧度)
        """
        c, s = np.cos(beta), np.sin(beta)
        return np.array([
            [ c, 0, s, 0],
            [ 0, 1, 0, 0],
            [-s, 0, c, 0],
            [ 0, 0, 0, 1]
        ])
    def transl(self,x, y, z):
        """
        说明：用于DH标定的(ETS模式)->平移的 4x4 齐次变换矩阵(米)
        """
        return np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ])
    def ets_fkine(self,q,ETS_LINK,FLIP_LIST):
        """
        说明：
        q：用于DH标定的(ETS模式)->ETS求正解
        ETS_LINK：ETS链表
        FLIP_LIST：ETS对应的正反轴，正为false，反为true
        """
        q= np.deg2rad(q)
        T = np.eye(4)
        for i,(x,y,z,rx,ry,rz) in enumerate(ETS_LINK):
            T_fixed = self.transl(x, y, z) @ self.rotx(rx) @ self.roty(ry) @ self.rotz(rz)
            theta = -q[i] if FLIP_LIST[i] else q[i]
            T_joint = self.rotz(theta)
            T = T @ T_fixed @ T_joint
        return T   
    def ets_plot_coordinate_frame(self,q,ETS_LINK,FLIP_LIST):
        """
        说明：ETS链表参数机器人可视化\n
        参数q：机器人关节角度(角度)\n
        参数ETS_LINK：默认或待优化的DH参数或ETS链表(List[]类型)\n
        参数FLIP_LIST：ETS链表对应的正反轴，正为false，反为true(List[]类型)\n
        返回值输出：无 -> 绘制图和打印
        """
        q = np.deg2rad(q)
        ets = ETS()
        for i,(x,y,z,rx,ry,rz) in enumerate(ETS_LINK):
            Link_ETS = ET.tx(x) * ET.ty(y) * ET.tz(z) * ET.Rx(rx) * ET.Ry(ry) * ET.Rz(rz) * ET.Rz(jindex=i,flip=FLIP_LIST[i])
            ets *= Link_ETS  
        T = ets.eval(q)   
        ets.teach(q)
        return T
    def psa_dh_calibrations_ets(self,n,joint_angles_,ge_n,ge_m,ETS_LINK,FLIP_LIST,
                                limit_xyz=0.01,limit_rx=0,limit_ry=1,limit_rz=1,
                                population=100,iters=120):
        """
        说明：用于DH标定的(ETS模式)->基于自适应精英变异的PSA优化算法DH参数标定\n
        参数n：机器人自由度n\n
        参数joint_angles：末端到达棋盘格指定数据点位时的关节角度（度），采样数据\n
        参数ge_n与ge_m：  格子数(n->x,m->y) 遵循右手坐标系，采样数据 \n
        参数ETS_LINK：默认或待优化的DH参数或ETS链表(List[]类型)\n
        参数FLIP_LIST：ETS链表对应的正反轴，正为false，反为true(List[]类型)\n
        参数limit_xyz、limit_rx、limit_ry、limit_rz：个体扰动范围设置\n
        参数population、iters：种群和迭代次数设置\n
        返回值输出：优化后的参数值
        """
        #n = 7                # 自由度n = 7轴
        N = population        # 种群个数N
        T = iters             # PSA迭代次数T 
        d = 6*n               # 维度d 其中d = 6xn 
        k = 0                 # 姿态权重->保证世界参考坐标系的姿态不动，而动(X,Y)位置，越大越表现越硬

        kp = 2                 # PSA -> kp
        ki = 0.5               # PSA -> ki
        kd = 1.2               # PSA -> kd
        t = 1                  # PSA -> t 当前迭代步
        f = np.zeros((N,1))    # PSA -> 种群适应度初始化
        LogT = np.log(T)       # PSA -> 自适应参数a的条件

        ## 个体扰动范围设置 ##
        xyz_lb , xyx_ub = [-limit_xyz] * 3 * n, [limit_xyz] * 3 * n   
        rx_lb ,rx_ub = [-limit_rx*np.pi/180]*n,[limit_rx*np.pi/180]*n   
        ry_lb ,ry_ub = [-limit_ry*np.pi/180]*n,[limit_ry*np.pi/180]*n  
        rz_lb ,rz_ub = [-limit_rz*np.pi/180]*(n-1),[limit_rz*np.pi/180]*(n-1)
        rzs_lb ,rzs_ub = [0],[0]
        lb = xyz_lb + rx_lb  + ry_lb + rz_lb + rzs_lb
        ub = xyx_ub + rx_ub  + ry_ub + rz_ub + rzs_ub

        def Initialization(N,d,lb,ub):  #PSA种群初始化
            ub = np.array(ub)
            lb = np.array(lb)
            if ub.size == 1 and lb.size == 1:
                # 所有变量具有相同边界的情况
                x = np.random.rand(N, d) * (ub - lb) + lb
                new_lb = np.full(d, lb)
                new_ub = np.full(d, ub)
            else:
                # 每个变量具有不同边界的情况
                x = np.zeros((N, d))
                for i in range(d):
                    ubi = ub[i]
                    lbi = lb[i]
                    x[:, i] = np.random.rand(N) * (ubi - lbi) + lbi
                new_lb = lb
                new_ub = ub
            return x, new_lb, new_ub
        def FindMinfAndindex(f): #寻找适应度最优的个体和对应的适应度
            index = np.argmin(f) #找适应度最优的个体
            targetF = f[index]   #根据索引找适应度最优值
            return targetF , index
        def PSA_LevyFlight(N,d): #莱维飞行机制函数
            beta = 1.5
            # 计算 Lévy 分布
            sigma = (math.gamma(1 + beta) * np.sin(np.pi * beta / 2) /
                    (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
            # Lévy 步长
            u = np.random.randn(N, d) * sigma
            v = np.random.randn(N, d)
            step = u / (np.abs(v) ** (1 / beta))
            
            return step
        def rotation_matrix_error(R0, R1):#姿态误差计算函数
            R_error = R0.T @ R1
            trace = np.trace(R_error)
            # Clip 防止数值误差导致 arccos 域错误
            cos_theta = (trace - 1) / 2
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            theta_rad = np.arccos(cos_theta)
            theta_deg = np.degrees(theta_rad)
            return theta_rad, theta_deg

        x, _, _ = Initialization(N,d,lb,ub)   
        lb_extended = np.tile(lb, (N, 1))  # R ∈ N * d  维度宽度扩展N
        ub_extended = np.tile(ub, (N, 1))  # R ∈ N * d  维度宽度扩展N

        #robotDH = np.array(DH.robotDH)     # 提取理想DH参数值 R ∈ n * 4  n=7 自由度
        robotDH = np.array(ETS_LINK)
        robotDH_flat = robotDH.flatten(order='F')  # R ∈ 1 * d 将DH参数的维度7x4按列优先级平铺为1*d 
        robotDH_after = robotDH_flat + x   # 对DH参数进行扰动

        Model0 = self.ets_fkine(joint_angles_[0],robotDH,FLIP_LIST)[0:3,3]    # 参考坐标原点 (x,y,z)
            
        ## PSA搜索算法初始化 ##
        P_Error_list  = []
        R_Error_list  = [] 
        for i in range(len(robotDH_after)):
            robotDH_after_ = robotDH_after[i].reshape((7, 6), order='F')      # DH变化后->按列恢复
            T0 = self.ets_fkine(joint_angles_[0],robotDH_after_,FLIP_LIST)    # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
            P0 = T0[0:3,3]                                                    # DH变化后->参考世界坐标原点位置坐标
            R0 = T0[0:3,0:3]                                                  # DH变化后->参考世界坐标原点旋转矩阵 (3x3)
            for j in range(len(joint_angles_)-1):
                joint_angles = joint_angles_[j+1] 
                T1 = self.ets_fkine(joint_angles ,robotDH_after_,FLIP_LIST)   # DH变化后->计算当前DH点的齐次变换矩阵 
                P1 = T1[0:3,3]                                                # DH变化后->参考点位置
                R1 = T1[0:3,0:3]                                              # DH变化后->参考点旋转矩阵 (3x3）
                
                P_Measure = [P0[0]-ge_n[j]*0.025 ,P0[1]-ge_m[j]*0.025,P1[2]]
                P_Error = (P1 - P_Measure)* 1000
            
                P_Error_list.append(P_Error)

                _,R_Error_Rad = rotation_matrix_error(R0,R1)
                R_Error_list.append(R_Error_Rad)

            P_Errors = np.array(P_Error_list)
            R_Errors = np.array(R_Error_list)

            P_Error_rmse = np.sqrt(np.mean(np.sum(P_Errors**2, axis=1)))  # 每次的平方和，再平均，再开方
            R_Error_rmse = np.mean(R_Errors)*k 
            P_R_Sum_Error = P_Error_rmse + R_Error_rmse
            f[i] = P_R_Sum_Error
            P_Error_list  = []
            R_Error_list  = []

        while t < T:
            if t == 1:
                [TargetF,index]= FindMinfAndindex(f)
                TargetX = x[index,:]
                newTargetX = TargetX
                newTargetF = TargetF
                Ek = TargetX - x
                Ek_1 = Ek
                Ek_2 = Ek
            else :
                Ek_2 = Ek_1 
                Ek_1 = Ek + newTargetX -TargetX
                Ek = newTargetX - x
                TargetX = newTargetX 
                TargetF = newTargetF    
            if t > 1:
                # 自适应柯西精英变异策略 #
                AEM_STD = np.std(np.abs((f-newTargetF)/newTargetF))
                if AEM_STD < 1e-2:
                    C=2
                elif AEM_STD < 1e-1:
                    C=1
                else:
                    C=0.5
                ri = np.abs(newTargetX-np.mean(x))
                rmax = np.abs(newTargetX - np.max(x))
                epsilon = 1e-8
                lamdar = 30
                x_m = (1 - ri/(rmax+epsilon)) * np.exp(-lamdar*t/T)
                sign_random = C * (2 * (np.random.rand(1, x.shape[1]) > 0.5) - 1)
                F_M = sign_random*(np.arctan(x_m)/np.pi)  
                F_M = np.squeeze(F_M)  
                x_trnd = newTargetX + stats.t.rvs(df=t) * newTargetX # 改进点： t分布公式扰动
                if t % 2 == 1:
                    # t 为奇数
                    new_xbest = newTargetX + F_M
                else:
                    # t 为偶数
                    new_xbest = newTargetX + F_M + x_trnd * t / T

                # 范围限制
                new_xbest = new_xbest < lb
                new_xbest = new_xbest > ub

                robotDH_after_new  = robotDH_flat + new_xbest  # 对DH参数进行扰动
                robotDH_after_new_ = robotDH_after_new.reshape((7, 6), order='F')    # DH变化后->按列恢复
                T0 = self.ets_fkine(joint_angles_[0],robotDH_after_new_,FLIP_LIST)   # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
                P0 = T0[0:3,3]                                                       # DH变化后->参考世界坐标原点位置坐标
                R0 = T0[0:3,0:3]                                                     # DH变化后->参考世界坐标原点旋转矩阵 (3x3)
                for j in range(len(joint_angles_)-1):
                    joint_angles = joint_angles_[j+1] 
                    T1 = self.ets_fkine(joint_angles ,robotDH_after_new_,FLIP_LIST)  # DH变化后->计算当前DH点的齐次变换矩阵 
                    P1 = T1[0:3,3]                                                   # DH变化后->参考点位置
                    R1 = T1[0:3,0:3]                                                 # DH变化后->参考点旋转矩阵 (3x3）
                     
                    P_Measure = [P0[0]-ge_n[j]*0.025 ,P0[1]-ge_m[j]*0.025,P1[2]]
                    P_Error = (P1 - P_Measure)* 1000
                
                    P_Error_list.append(P_Error)

                    _,R_Error_Rad = rotation_matrix_error(R0,R1)
                    R_Error_list.append(R_Error_Rad)

                P_Errors = np.array(P_Error_list)
                R_Errors = np.array(R_Error_list)

                P_Error_rmse = np.sqrt(np.mean(np.sum(P_Errors**2, axis=1)))  # 每次的平方和，再平均，再开方
                R_Error_rmse = np.mean(R_Errors)*k
                P_R_Sum_Error = P_Error_rmse + R_Error_rmse
                new_fbest = P_R_Sum_Error
                P_Error_list  = []
                R_Error_list  = []
                if new_fbest< newTargetF:
                    newTargetF = new_fbest
                    newTargetX = new_xbest               
                # 变异结束 #
                                      
            a = (np.log(T-t+2)/LogT) ** 2
            out0 = (np.cos(1-t/T)+ a * np.random.rand(N, d) * PSA_LevyFlight(N,d)) * Ek
            pid = np.random.rand(N, 1) * kp * (Ek- Ek_1) + np.random.rand(N, 1) * ki * Ek +np.random.rand(N, 1)*kd*(Ek-2*Ek_1+Ek_2)

            r = np.random.rand(N, 1) * np.cos(t/T)
            x = x + r*pid + (1-r)*out0
            
            lbViolated = x < lb_extended
            ubViolated = x > ub_extended

            x[lbViolated] = lb_extended[lbViolated]
            x[ubViolated] = ub_extended[ubViolated]

            robotDH_after = robotDH_flat + x           # 对DH参数进行扰动
            P_Errors = []
            R_Errors = [] 
            f = np.zeros((N,1))
            for i in range(len(robotDH_after)):
                robotDH_after_ = robotDH_after[i].reshape((7, 6), order='F')       # DH变化后->按列恢复
                T0 = self.ets_fkine(joint_angles_[0],robotDH_after_,FLIP_LIST)     # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
                P0 = T0[0:3,3]                                                     # DH变化后->参考世界坐标原点位置坐标
                R0 = T0[0:3,0:3]                                                   # DH变化后->参考世界坐标原点旋转矩阵 (3x3)
                for j in range(len(joint_angles_)-1):
                    joint_angles = joint_angles_[j+1] 
                    T1 = self.ets_fkine(joint_angles ,robotDH_after_,FLIP_LIST)    # DH变化后->计算当前DH点的齐次变换矩阵 
                    P1 = T1[0:3,3]                                                 # DH变化后->参考点位置
                    R1 = T1[0:3,0:3]                                               # DH变化后->参考点旋转矩阵 (3x3）
                    
                    P_Measure = [P0[0]-ge_n[j]*0.025 ,P0[1]-ge_m[j]*0.025,P1[2]]
                    P_Error = (P1 - P_Measure)* 1000
                
                    P_Error_list.append(P_Error)

                    R_Error_Rad,_ = rotation_matrix_error(R0,R1)
                    R_Error_list.append(R_Error_Rad)

                P_Errors = np.array(P_Error_list)
                R_Errors = np.array(R_Error_list)

                P_Error_rmse = np.sqrt(np.mean(np.sum(P_Errors**2, axis=1)))  # 每次的平方和，再平均，再开方
                R_Error_rmse = np.mean(R_Errors)*k
                P_R_Sum_Error = P_Error_rmse + R_Error_rmse
                f[i] = P_R_Sum_Error
                P_Error_list  = []
                R_Error_list  = []
            if np.min(f)<newTargetF:
                [newTargetF ,index ] = FindMinfAndindex(f)
                newTargetX = x[index,:]
            print(f"当前步数:{t}次的最优值={newTargetF}")
            t  = t + 1 
        
        ## 输出 ##
        robotDH_after = robotDH_flat + newTargetX   # 对DH参数进行扰动
        errors = []
        robotDH_after_ = robotDH_after.reshape((7, 6), order='F')  # DH变化后->按列恢复
        Model0 = self.ets_fkine(joint_angles_[0],robotDH_after_,FLIP_LIST)[0:3,3]  # DH变化后->参考坐标原点
       
        for j in range(len(joint_angles_)-1):
            joint_angles = joint_angles_[j+1]                         # 机械臂当前角度值(需要采集)
            Model0_ = self.ets_fkine(joint_angles,robotDH_after_,FLIP_LIST)[0:3,3] # 理想值(x,y,z) 
            Measure = [Model0[0]-ge_n[j]*0.025 , Model0[1]-ge_m[j]*0.025, Model0_[2]]  # 测量值(x,y,z) 
            error = (Model0_ - np.array(Measure)) * 1000  # 单位：mm
            errors.append(error)
        errors = np.array(errors)

        print(f"优化后的测量与模型误差：\n {errors} mm")  
        print(f"优化后RMSE均分根误差为:{newTargetF}mm") 
        print(f"优化后的参数为:") 
        for row in robotDH_after_:
            print("[ " + ", ".join(f"{v: .6f}" for v in row) + " ],")
        return robotDH_after_
    #DH模式
    def _dh_transform(self,theta , alpha , r ,d):
        return np.array([
            [np.cos(theta), -np.sin(theta) * np.cos(alpha), np.sin(theta) * np.sin(alpha), r * np.cos(theta)],
            [np.sin(theta), np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), r * np.sin(theta)],
            [0, np.sin(alpha), np.cos(alpha), d],
            [0, 0, 0, 1]
        ])
    def dh_fkine(self,joint_angles, robotDH_,unit='degrees'):
        """
        说明：
        q：用于DH标定的(标准DH模式)->DH值求正解\n
        joint_angles：角度值(度)\n
        robotDH：机器人DH参数 n*4 n为自由度 规格顺序为# theta , alpha , a, d
        返回值：末端齐次变换矩阵
        """
        if len(joint_angles) != 7:
            raise ValueError("joint_angles must be a list or array of 7 elements")

        if unit == 'degrees':
            joint_angles = np.deg2rad(joint_angles)
        elif unit == 'radians':
            pass

        T = np.eye(4)  
        for i in range(7):
            theta , alpha , r ,d = robotDH_[i]
            #d, theta, r, alpha = robotDH[i]
            theta += joint_angles[i]
            A = self._dh_transform(theta , alpha , r ,d)  
            T = np.dot(T, A) 
        T = np.round(T, 4)
        return T
    def psa_dh_calibrations(self,n,joint_angles_,ge_n,ge_m,robot_dh):
        """
        说明：用于DH标定的(标准DH模式)->基于自适应精英变异的PSA优化算法DH参数标定\n
        参数n：机器人自由度n\n
        参数joint_angles：末端到达棋盘格指定数据点位时的关节角度（度），采样数据\n
        参数ge_n与ge_m：  格子数(n->x,m->y) 遵循右手坐标系，采样数据 \n
        参数robot_dh：默认或待优化的DH参数(List[]类型)\n
        返回值输出：优化后的参数值
        """
        #n = 7                 # 自由度n = 7轴
        N = 100                # 种群个数N
        T = 300                # PSA迭代次数T 
        d = 4*n                # 维度d 其中d = 4xn
        k = 0                  # 姿态权重->保证世界参考坐标系的姿态不动，而动(X,Y)位置，越大越表现越硬

        kp = 2                 # PSA -> kp
        ki = 0.5               # PSA -> ki
        kd = 1.2               # PSA -> kd
        t = 1                  # PSA -> t 当前迭代步
        f = np.zeros((N,1))    # PSA -> 种群适应度初始化
        LogT = np.log(T)       # PSA -> 自适应参数a的条件

        ## 个体扰动范围设置 ##
        length_lb , length_ub = [0.0001] *2* n, [-0.0001] *2* n           # [length_lb,length_ub]=[下限,上限] 个体扰动范围  
        angle_lb,angle_ub = [-10*np.pi/180]* (n-1), [10*np.pi/180]* (n-1) # [angle_lb,angle_ub]=[下限,上限] 个体扰动范围
        angle_lb_end  , angle_ub_end = [-0*np.pi/180],[0*np.pi/180] 
        angle_lba,angle_uba = [-0.5*np.pi/180]* n, [0.5*np.pi/180]* n     # [angle_lb,angle_ub]=[下限,上限] 个体扰动范围 
        ub = angle_ub + angle_ub_end + angle_uba + length_ub
        lb = angle_lb + angle_lb_end + angle_lba + length_lb
        newTargetF= 0

        def Initialization(N,d,lb,ub):  #PSA种群初始化
            ub = np.array(ub)
            lb = np.array(lb)
            if ub.size == 1 and lb.size == 1:
                # 所有变量具有相同边界的情况
                x = np.random.rand(N, d) * (ub - lb) + lb
                new_lb = np.full(d, lb)
                new_ub = np.full(d, ub)
            else:
                # 每个变量具有不同边界的情况
                x = np.zeros((N, d))
                for i in range(d):
                    ubi = ub[i]
                    lbi = lb[i]
                    x[:, i] = np.random.rand(N) * (ubi - lbi) + lbi
                new_lb = lb
                new_ub = ub
            return x, new_lb, new_ub
        def FindMinfAndindex(f): #寻找适应度最优的个体和对应的适应度
            index = np.argmin(f) #找适应度最优的个体
            targetF = f[index]   #根据索引找适应度最优值
            return targetF , index
        def PSA_LevyFlight(N,d): #莱维飞行机制函数
            beta = 1.5
            # 计算 Lévy 分布
            sigma = (math.gamma(1 + beta) * np.sin(np.pi * beta / 2) /
                    (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
            # Lévy 步长
            u = np.random.randn(N, d) * sigma
            v = np.random.randn(N, d)
            step = u / (np.abs(v) ** (1 / beta))
            
            return step
        def rotation_matrix_error(R0, R1):#姿态误差计算函数
            R_error = R0.T @ R1
            trace = np.trace(R_error)
            # Clip 防止数值误差导致 arccos 域错误
            cos_theta = (trace - 1) / 2
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            theta_rad = np.arccos(cos_theta)
            theta_deg = np.degrees(theta_rad)
            return theta_rad, theta_deg

        x, _, _ = Initialization(N,d,lb,ub)   
        lb_extended = np.tile(lb, (N, 1))  # R ∈ N * d  维度宽度扩展N
        ub_extended = np.tile(ub, (N, 1))  # R ∈ N * d  维度宽度扩展N

        #robotDH = np.array(DH.robotDH)     # 提取理想DH参数值 R ∈ n * 4  n=7 自由度
        robotDH = np.array(robot_dh)
        robotDH_flat = robotDH.flatten(order='F')  # R ∈ 1 * d 将DH参数的维度7x4按列优先级平铺为1*d 
        robotDH_after = robotDH_flat  + x # DH参数
        
        ## 测试输入 ##
        errors = []
        robotDH_after_ = robotDH_flat.reshape((7, 4), order='F')  # DH变化后->按列恢复
        Model0 = self.dh_fkine(joint_angles_[0],robotDH_after_)[0:3,3]  # DH变化后->参考坐标原点
        for j in range(len(joint_angles_)-1):
            joint_angles = joint_angles_[j+1]                         # 机械臂当前角度值(需要采集)
            Model0_ = self.dh_fkine(joint_angles,robotDH_after_)[0:3,3] # 理想值(x,y,z) 
            Measure = [Model0[0]-ge_n[j]*0.025 , Model0[1]-ge_m[j]*0.025, Model0_[2]]  # 测量值(x,y,z) 
            error = (Model0_ - np.array(Measure)) * 1000  # 单位：mm
            errors.append(error)
        errors = np.array(errors)
        print(f"优化前的测量与模型误差：\n {errors} mm")  
        
        ## PSA搜索算法初始化 ##
        P_Error_list  = []
        R_Error_list  = [] 
        f = np.zeros((N, 1))
        for i in range(len(robotDH_after)):
            if i==0:
                robotDH_after_ = robotDH_flat.reshape((7, 4), order='F')   # DH变化后->按列恢复
                T0 = self.dh_fkine(joint_angles_[0],robotDH_after_)            # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
                P0 = T0[0:3,3]                                                 # DH变化后->参考世界坐标原点位置坐标
                R0 = T0[0:3,0:3]                                               # DH变化后->参考世界坐标原点旋转矩阵 (3x3)
            else:
                robotDH_after_ = robotDH_after[i].reshape((7, 4), order='F')   # DH变化后->按列恢复
                T0 = self.dh_fkine(joint_angles_[0],robotDH_after_)            # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
                P0 = T0[0:3,3]                                                 # DH变化后->参考世界坐标原点位置坐标
                R0 = T0[0:3,0:3]                                               # DH变化后->参考世界坐标原点旋转矩阵 (3x3)

            for j in range(len(joint_angles_)-1):
                joint_angles = joint_angles_[j+1] 
                T1 = self.dh_fkine(joint_angles ,robotDH_after_)           # DH变化后->计算当前DH点的齐次变换矩阵 
                P1 = T1[0:3,3]                                             # DH变化后->参考点位置
                R1 = T1[0:3,0:3]                                           # DH变化后->参考点旋转矩阵 (3x3）
                
                P_Measure = [P0[0]-ge_n[j]*0.025 ,P0[1]-ge_m[j]*0.025,P1[2]]
                P_Error = (P1 - P_Measure)* 1000
            
                P_Error_list.append(P_Error)

                R_Error_Rad,_ = rotation_matrix_error(R0,R1)
                R_Error_list.append(R_Error_Rad)

            P_Errors = np.array(P_Error_list)
            R_Errors = np.array(R_Error_list)

            P_Error_rmse = np.sqrt(np.mean(np.sum(P_Errors**2, axis=1)))  # 每次的平方和，再平均，再开方
            R_Error_rmse = np.mean(R_Errors)*k 
            P_R_Sum_Error = P_Error_rmse + R_Error_rmse
            f[i] = P_R_Sum_Error
            P_Error_list  = []
            R_Error_list  = []

        while t < T:
            
            if t == 1:
                [TargetF,index]= FindMinfAndindex(f)
                TargetX = x[index,:]
                newTargetX = TargetX
                newTargetF = TargetF
                Ek = TargetX - x
                Ek_1 = Ek
                Ek_2 = Ek
            else :
                Ek_2 = Ek_1 
                Ek_1 = Ek + newTargetX -TargetX
                Ek = newTargetX - x
                TargetX = newTargetX 
                TargetF = newTargetF
            if t > 1:
                 # 自适应柯西精英变异策略 #
                AEM_STD = np.std(np.abs((f-newTargetF)/newTargetF))
                if AEM_STD < 1e-2:
                    C=2
                elif AEM_STD < 1e-1:
                    C=1
                else:
                    C=0.5
                ri = np.abs(newTargetX-np.mean(x))
                rmax = np.abs(newTargetX - np.max(x))
                epsilon = 1e-8
                lamdar = 30
                x_m = (1 - ri/(rmax+epsilon)) * np.exp(-lamdar*t/T)
                sign_random = C * (2 * (np.random.rand(1, x.shape[1]) > 0.5) - 1)
                F_M = sign_random*(np.arctan(x_m)/np.pi)     
                F_M = np.squeeze(F_M) 
                x_trnd = newTargetX + stats.t.rvs(df=t) * newTargetX # 改进点： t分布公式扰动
                if t % 2 == 1:
                    # t 为奇数
                    new_xbest = newTargetX + F_M
                else:
                    # t 为偶数
                    new_xbest = newTargetX + F_M + x_trnd * t / T
                robotDH_after_new  = robotDH_flat + new_xbest  # 对DH参数进行扰动
                robotDH_after_new_ = robotDH_after_new.reshape((7, 4), order='F')    # DH变化后->按列恢复
                T0 = self.dh_fkine(joint_angles_[0],robotDH_after_new_)   # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
                P0 = T0[0:3,3]                                                       # DH变化后->参考世界坐标原点位置坐标
                R0 = T0[0:3,0:3]                                                     # DH变化后->参考世界坐标原点旋转矩阵 (3x3)
                for j in range(len(joint_angles_)-1):
                    joint_angles = joint_angles_[j+1] 
                    T1 = self.dh_fkine(joint_angles ,robotDH_after_new_)  # DH变化后->计算当前DH点的齐次变换矩阵 
                    P1 = T1[0:3,3]                                                   # DH变化后->参考点位置
                    R1 = T1[0:3,0:3]                                                 # DH变化后->参考点旋转矩阵 (3x3）
                     
                    P_Measure = [P0[0]-ge_n[j]*0.025 ,P0[1]-ge_m[j]*0.025,P1[2]]
                    P_Error = (P1 - P_Measure)* 1000
                
                    P_Error_list.append(P_Error)

                    _,R_Error_Rad = rotation_matrix_error(R0,R1)
                    R_Error_list.append(R_Error_Rad)

                P_Errors = np.array(P_Error_list)
                R_Errors = np.array(R_Error_list)

                P_Error_rmse = np.sqrt(np.mean(np.sum(P_Errors**2, axis=1)))  # 每次的平方和，再平均，再开方
                R_Error_rmse = np.mean(R_Errors)*k
                P_R_Sum_Error = P_Error_rmse + R_Error_rmse
                new_fbest = P_R_Sum_Error
                P_Error_list  = []
                R_Error_list  = []
                if new_fbest< newTargetF:
                    newTargetF = new_fbest
                    newTargetX = new_xbest               
            # 变异结束 #
            a = (np.log(T-t+2)/LogT) ** 2
            out0 = (np.cos(1-t/T)+ a * np.random.rand(N, d) * PSA_LevyFlight(N,d)) * Ek
            pid = np.random.rand(N, 1) * kp * (Ek- Ek_1) + np.random.rand(N, 1) * ki * Ek +np.random.rand(N, 1)*kd*(Ek-2*Ek_1+Ek_2)

            r = np.random.rand(N, 1) * np.cos(t/T)
            x = x + r*pid + (1-r)*out0
            
            lbViolated = x < lb_extended
            ubViolated = x > ub_extended

            x[lbViolated] = lb_extended[lbViolated]
            x[ubViolated] = ub_extended[ubViolated]

            robotDH_after = robotDH_flat + x   # 对DH参数进行扰动
            P_Errors = []
            R_Errors = [] 
            f = np.zeros((N,1))
            for i in range(len(robotDH_after)):
                    robotDH_after_ = robotDH_after[i].reshape((7, 4), order='F')   # DH变化后->按列恢复
                    T0 = self.dh_fkine(joint_angles_[0],robotDH_after_)              # DH变化后->计算当前DH的世界坐标原点的齐次变换矩阵
                    P0 = T0[0:3,3]                                                 # DH变化后->参考世界坐标原点位置坐标
                    R0 = T0[0:3,0:3]                                               # DH变化后->参考世界坐标原点旋转矩阵 (3x3)
                    for j in range(len(joint_angles_)-1):
                        joint_angles = joint_angles_[j+1] 
                        T1 = self.dh_fkine(joint_angles ,robotDH_after_)             # DH变化后->计算当前DH点的齐次变换矩阵 
                        P1 = T1[0:3,3]                                             # DH变化后->参考点位置
                        R1 = T1[0:3,0:3]                                           # DH变化后->参考点旋转矩阵 (3x3）
                        
                        P_Measure = [P0[0]-ge_n[j]*0.025 ,P0[1]-ge_m[j]*0.025,P1[2]]
                        P_Error = (P1 - P_Measure)* 1000
                    
                        P_Error_list.append(P_Error)

                        R_Error_Rad,_ = rotation_matrix_error(R0,R1)
                        R_Error_list.append(R_Error_Rad)

                    P_Errors = np.array(P_Error_list)
                    R_Errors = np.array(R_Error_list)
                    
                    P_Error_rmse = np.sqrt(np.mean(np.sum(P_Errors**2, axis=1)))  # 每次的平方和，再平均，再开方
                    R_Error_rmse = np.mean(R_Errors)*k
                    P_R_Sum_Error = P_Error_rmse + R_Error_rmse
                    f[i] = P_R_Sum_Error
                    P_Error_list  = []
                    R_Error_list  = []   
                                   
            if np.min(f)< newTargetF:
                    [newTargetF ,index ] = FindMinfAndindex(f)
                    newTargetX = x[index,:]

            print(f"当前步数:{t}次的最优值{newTargetF}")
            t  = t + 1 
        
        ## 测试输出 ##
        robotDH_after = robotDH_flat + newTargetX  # 对DH参数进行扰动
        errors = []
        robotDH_after_ = robotDH_after.reshape((7, 4), order='F')       # DH变化后->按列恢复
        Model0 = self.dh_fkine(joint_angles_[0],robotDH_after_)[0:3,3]  # DH变化后->参考坐标原点
        for j in range(len(joint_angles_)-1):
            joint_angles = joint_angles_[j+1]                           # 机械臂当前角度值(需要采集)
            Model0_ = self.dh_fkine(joint_angles,robotDH_after_)[0:3,3] # 理想值(x,y,z) 
            Measure = [Model0[0]-ge_n[j]*0.025 , Model0[1]-ge_m[j]*0.025, Model0_[2]]  # 测量值(x,y,z) 
            error = (Model0_ - np.array(Measure)) * 1000  # 单位：mm
            errors.append(error)
        errors = np.array(errors)

        print(f"优化后的测量与模型误差：\n {errors} mm")  
        print(f"优化后RMSE均分根误差为:{newTargetF}mm") 
        print(f"优化后的参数为:") 
        for row in robotDH_after_:
            print("[ " + ", ".join(f"{v: .6f}" for v in row) + " ],")
        return robotDH_after_

class RobotCoordinatePlot(ABC):
    """机器人坐标轴绘制类"""
    def _draw_coordinate_frame(self,ax, T, name='', length=0.1):
        """绘制单个坐标系：以变换矩阵T为基础，绘制三个方向的箭头"""
        origin = T[:3, 3]
        x_axis = T[:3, 0] * length
        y_axis = T[:3, 1] * length
        z_axis = T[:3, 2] * length

        ax.quiver(*origin, *x_axis, color='r')
        ax.quiver(*origin, *y_axis, color='g')
        ax.quiver(*origin, *z_axis, color='b')
        ax.text(*origin, name, color='k')  
    def _rotation_matrix_error_xyz(self,R0, R1):
        """
        说明：用于计算两个旋转矩阵之间的误差\n
        返回值：(弧度误差 ，角度误差)
        """
        R_rel = R0.T @ R1
        rot = R.from_matrix(R_rel)
        # 选择欧拉角顺序（常用为 'xyz' 或 'zyx'）
        euler_angles_rad = rot.as_euler('xyz', degrees=False)
        euler_angles_deg = np.degrees(euler_angles_rad)
        return euler_angles_rad, euler_angles_deg 
    def coordinate_plot(self,T_list):
        """
        说明：机器人坐标系绘制\n
        输入：T_list为T齐次变换矩阵列表List[List[]]
        返回值：绘制图和打印
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        # 设置坐标轴范围和标签
        ax.set_xlim([-0.5, 0.5])
        ax.set_ylim([-0.5, 0.5])
        ax.set_zlim([-0.5, 0.5])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # 绘制世界坐标系
        T_world = np.eye(4)
        self._draw_coordinate_frame(ax, T_world, name='World')
        
        # 动态绘制 T_list 中的每个坐标系
        for i, T in enumerate(T_list):
            frame_name = f"T{i+1}"  # 自动生成名称 T1, T2, T3...
            self._draw_coordinate_frame(ax, T, name=frame_name)      
        plt.show()  
    def two_coordinate_plot(self,T1,T2):
        """
        说明：机器人坐标系绘制示例\n
        输入：T1和T2 4x4齐次变换矩阵
        返回值：绘制图和打印
        """
        T_list=[]
        T_list.append(T1)
        T_list.append(T2)
        # R_Error_rad,_ = self._rotation_matrix_error_xyz(T1[:3,:3],T2[:3,:3])
        # print(f"参考T1:\n{T1} \n优化后T2:\n {T2}")
        # print(f"位置误差{(T1-T2)[:3,3]*100}cm,\n姿态误差{ np.rad2deg (R_Error_rad)}°")
        self.coordinate_plot(T_list)

# 2025.7.2 9:04更新
import json
import socket
import zlib
import struct
import select
import threading
import logging
from typing import Dict, Any, Optional, List, Union
class RobotArmController(ABC):
    """机器人控制器类，封装所有通信和控制功能\n
    说明：有6001端口和7000端口\n
    6001用于初始化、上电操作以及读取关节角度\n
    7000用于多关节角序列控制\n
    """
    # 数据帧头
    FRAME_HEADER = b'\x4e\x66'
    # 清错
    FAULT_RESET = b'\x32\x01'
    # 伺服
    SERVO_STATUS_SET = b'\x20\x01'
    SERVO_STATUS_INQUIRE = b'\x20\x02'
    # 模式
    OPERATION_MODE_SET = b'\x21\x01'
    OPERATION_MODE_INQUIRE = b'\x21\x02'
    # 上下电
    DEADMAN_STATUS_SET = b'\x23\x01'
    DEADMAN_STATUS_INQUIRE = b'\x23\x02'
    # 作业控制
    JOBSEND_DONE = b'\x25\x01'
    STOP_JOB_RUN = b'\x25\x03'
    # 速度
    SPEED_SET = b'\x26\x01'
    SPEED_INQUIRE = b'\x26\x02'
    # 当前关节角度查询
    CURRENTPOS_INQUIRE = b'\x2a\x02'
    # 单点移动
    ROBOTMOVEJOINT = b'\x45\x01'
    # 多点轨迹
    MULTI_POINT = b'\x95\x21' 
    def __init__(self, ip: str, port: int):
        """
        初始化控制器
        :param ip: 机械臂IP地址
        :param port: 机械臂端口号
        """
        self.ip = ip
        self.port = port
        self.socket: Optional[socket.socket] = None
        self._connect_flag = False  # 连接状态标志
        self.return_status: Dict[str, Any] = {}  # 状态存储字典
        self._receive_thread: Optional[threading.Thread] = None
        self._status_lock = threading.Lock()
        self._setup_logger()
    def _setup_logger(self):
        """配置日志记录器"""
        self.logger = logging.getLogger('RobotController')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    def __enter__(self):
        """支持with上下文管理器"""
        self.connect()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出时自动断开连接"""
        self.disconnect()
    def connect(self) -> bool:
        """建立控制器连接"""
        try:
            self.socket = socket.socket()
            self.socket.connect((self.ip, self.port))
            self._connect_flag = False
            self._start_receive_thread()
            self.logger.info(f"成功连接到 {self.ip}:{self.port}")
            return True
        except socket.error as e:
            self.logger.error(f"连接失败: {e}")
            return False
    def disconnect(self):
        """断开连接并清理资源"""
        self._connect_flag = True
        if self.socket:
            self.socket.close()
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=2)
        self.logger.info("连接已断开")
    def reconnect(self, retries=3, delay=1):
        """自动重连机制"""
        for attempt in range(retries):
            try:
                self.disconnect()
                self.connect()
                self.logger.info(f"第{attempt+1}次重连成功")
                return True
            except Exception as e:
                self.logger.warning(f"重连失败: {e}")
                time.sleep(delay)
        return False
    def _start_receive_thread(self):
        """启动数据接收线程"""
        self._receive_thread = threading.Thread(
            target=self._receive_loop, 
            daemon=True
        )
        self._receive_thread.start()
    def _receive_loop(self):
        """接收数据的线程循环"""
        while True:
            if self._connect_flag or not self.socket:
                break
            try:
                while not self._connect_flag and self.socket:
                    try:
                        readable, _, _ = select.select([self.socket], [], [], 1)
                        if readable:
                            data = self.socket.recv(1024)
                            if data:
                                self._parse_status(data)
                    except (OSError, ConnectionAbortedError):
                        break
            except Exception as e:
                self.logger.error(f"接收线程异常: {e}")
                break
    def _crc(self, data_to: bytes, command: bytes, data_segment: str) -> bytes:
        """CRC校验计算（私有方法）"""
        length_bytes = struct.pack('>H', len(data_segment))
        crc32 = zlib.crc32(length_bytes + command + data_segment)
        crc_bytes = struct.pack('>I', crc32)
        return data_to + length_bytes + command + data_segment + crc_bytes
    def _send_json_command(self, cmd: bytes, json_data: str, keynames: List[str]):
        """
        发送JSON命令并等待响应
        :param cmd: 命令字节
        :param json_data: JSON格式数据字符串
        :param keynames: 需要等待的状态键名列表
        """
        if not self.socket:
            raise ConnectionError("未建立有效连接")

        try:
            data = self._crc(self.FRAME_HEADER, cmd, json_data.encode("GBK"))
            self.socket.send(data)
        except (BrokenPipeError, ConnectionResetError) as e:
            self.logger.error(f"命令发送失败: {e}")
            self.reconnect()
            return
        
        time.sleep(0.1)  # 根据实际需求调整
        
        # 等待所有需要的状态返回
        missing_keys = [key for key in keynames if key not in self.return_status]
        while missing_keys:
            self.logger.debug(f"等待状态键: {missing_keys}")
            time.sleep(0.1)
            missing_keys = [key for key in keynames if key not in self.return_status]
    def _parse_status(self, data: bytes):
        """解析状态数据（私有方法）"""
        with self._status_lock:
            header = data[:6]
            data_length = header[2] * 256 + header[3]
            cmd_word = f"{data[4]:02X}{data[5]:02X}"
            
            json_data = data[6:6 + data_length].decode('utf-8').strip()
            try:
                parsed = json.loads(json_data)
                for key, value in parsed.items():
                    status_key = cmd_word + key
                    self.return_status[status_key] = value
                self.logger.debug(f"状态更新: {self.return_status}")
            except json.JSONDecodeError:
                self.logger.error("JSON解析失败")      
    def fault_reset(self, robot: int) -> bool:
        """
        伺服清除错误指令
        :param robot:机器人号码
        :return: 清错成功返回true, 清除失败发挥false
        """
        json_data = f'{{"robot":{robot}}}'
        self._send_json_command(self.FAULT_RESET, json_data, ['3202clearErrflag'])
        return self.return_status.get('3202clearErrflag', False)
    def servo_status_set(self, robot: int, status: int) -> int:
        """
        伺服状态设置
        :param robot:机器人号码
        :param status:  0:停⽌, 1:就绪, 2:错误, 3:运⾏
        :return:  0:停⽌, 1:就绪, 2:错误, 3:运⾏
        """
        json_data = f'{{"robot":{robot},"status":{status}}}'
        self._send_json_command(self.SERVO_STATUS_SET, json_data, ['2003status'])
        return self.return_status.get('2003status', 0)
    def servo_status_inquire(self, robot: int) -> int:
        """
        伺服状态查询
        :param robot:机器人号码
        :return:  0:停⽌, 1:就绪, 2:错误, 3:运⾏
        """
        json_data = f'{{"robot":{robot}}}'
        self._send_json_command(self.SERVO_STATUS_INQUIRE, json_data, ['2003status'])
        status = self.return_status.get('2003status', 0)
        status_map = {
            0: "伺服停止",
            1: "伺服就绪",
            2: "伺服错误",
            3: "伺服运行"
        }
        self.logger.info(f"伺服状态: {status_map.get(status, '未知状态')}")
        return status
    def operation_mode_set(self, mode: int) -> int:
        """
        示教，运行，远程模式切换
        :param mode: 0:⽰教模式(Teach), 1:远程模式(Circle), 2:运⾏模式(Repeat)
        :return: 无返回值
        """
        json_data = f'{{"mode":{mode}}}'
        self._send_json_command(self.OPERATION_MODE_SET, json_data, ['2103mode'])
        return self.return_status.get('2103mode', 0)
    def operation_mode_query(self) -> int:
        """查询操作模式"""
        self._send_json_command(self.OPERATION_MODE_INQUIRE, '{}', ['2103mode'])
        mode = self.return_status.get('2103mode', 0)
        mode_names = ["示教模式", "远程模式", "运行模式"]
        self.logger.info(f"当前模式: {mode_names[mode] if mode <3 else '未知模式'}")
        return mode
    def jobsend_done(self, robot: int, jobname: str, line: int, continue_run: int) -> int:
        """
        运行作业文件
        :param robot: 机器人号码
        :param jobname: 作业文件名字
        :param line: 作业⽂件指令⾏数,不能为零，不能超过总⾏数
        :param continueRun: 1:继续运⾏,0:不继续运⾏
        :return: 无返回值
        """
        json_data = f'{{"robot":{robot},"jobname":"{jobname}","line":{line},"continueRun":{continue_run}}}'
        self._send_json_command(self.JOBSEND_DONE, json_data, ['2B04kind'])
        return self.return_status.get('2B04kind', 0)
    def stop_job_run(self, robot: int) -> int:
        """停止作业运行"""
        json_data = f'{{"robot":{robot}}}'
        self._send_json_command(self.STOP_JOB_RUN, json_data, ['3D03status'])
        return self.return_status.get('3D03status', 0)
    def speed_set(self, robot: int, speed: int) -> int:
        """
        设置全局速度
        :param robot: 机器人号码
        :param speed: 全局速度设置   0-100
        :return: 控制器返回的速度   0-100
        """
        if not 0 <= speed <= 100:
            raise ValueError("速度值必须在0-100之间")
        json_data = f'{{"robot":{robot},"speed":{speed}}}'
        self._send_json_command(self.SPEED_SET, json_data, ['2603speed'])
        return self.return_status.get('2603speed', 0)
    def speed_inquire(self, robot: int) -> int:
        """查询全局速度"""
        json_data = f'{{"robot":{robot}}}'
        self._send_json_command(self.SPEED_INQUIRE, json_data, ['2603speed'])
        speed = self.return_status.get('2603speed', 0)
        self.logger.info(f"当前速度: {speed}%")
        return speed
    def currentpos_inquiry(self, robot: int, coord: int) -> List[float]:
        """
        查询当前位置
        :param robot: 机器人号码
        :param coord: 0:关节坐标系, 1:直⻆, 2:⼯具, 3:⽤⼾
        :param pos: 需要查询你的坐标系。pos是弧度位置, posDeg是角度位置。默认是pos
        :return:[1.1,2.2,3.3,4.4,5.5,6.6,7.7]。如果是关节坐标分别代表1-7关节,
        直角坐标系分别x,y,z,a,b,c。工具、用户同直角。
        直角坐标系下第七位参数默认为0即可。
        """
        json_data = f'{{"robot":{robot},"coord":{coord}}}'
        self._send_json_command(self.CURRENTPOS_INQUIRE, json_data, ['2A03pos'])
        position = self.return_status.get('2A03pos', [0.0]*7)
        #self.logger.info(f"当前位置: {position}")
        return position
    def multi_point_move(self, target_vecs: List[List[float]]):
        """
        说明：7000端口多点-轨迹运动\n
        参数target_vecs：输入List[List[]]类型\n
        target_vecs
        =[\n
         [1,1,1,1,1,1,1],\n
         [2,2,3,4,5,6,6],\n
         ............... \n
         ]
        """
        cfgs = '{ "coord": "ACS", "extMove": 0, "sync": 0, "speed": 100, "acc": 100, "pl": 5, "moveMode": "MOVC" }'
        targets = "[" + ",".join(
            f'{{"pos": {json.dumps(pos, separators=(",", ":"))}}}' 
            for pos in target_vecs
        ) + "]"
        cmd_data = f'{{ "robot": 1, "clearBuffer": 1, "targetMode": 0, "cfg": {cfgs}, "targetVec": {targets} }}'
        
        if self.socket:
            packed_data = self._crc(self.FRAME_HEADER, self.MULTI_POINT, cmd_data.encode("GBK"))
            self.socket.send(packed_data)
           # self.logger.info("已发送多点移动指令")
    def robotsdk_init(self,controllerSocket6001,FileName):
        """
        说明：SDK初始化，以6001端口启动\n
        参数controllerSocket6001：连接后的Socket6001\n
        参数FileName：需要打开的工程文件"name"(str类型)
        """
        servo_flag = controllerSocket6001.servo_status_inquire(1)
        while servo_flag!=3:
            print("\n正在初始化...\n")
            # 切换模式，先示教模式
            controllerSocket6001.operation_mode_set(0)  
            # 清错
            controllerSocket6001.fault_reset(1)
            # 伺服就绪
            controllerSocket6001.servo_status_set(1, 1)
            # 再切换运行模式
            controllerSocket6001.operation_mode_set(2)
            # 设置全局速度
            controllerSocket6001.speed_set(1, 60)
            # 全局速度查询
            controllerSocket6001.speed_inquire(1)
            # 运行作业文件
            #controllerSocket6001.jobsend_done(1, FileName, 1, 1)
            servo_flag = controllerSocket6001.servo_status_inquire(1)
            if servo_flag==3:
                print("\n初始化结束!!\n")

from geometry_msgs.msg import PoseStamped
class RobotArmMathematical(ABC):
    def matrixToEuler(self, T):
        """
        说明：将齐次变换矩阵转换为欧拉角 (Yaw, Pitch, Roll)，旋转顺序为 ZYX。\n
        Args: T (numpy.ndarray): 齐次变换矩阵 (4x4)。\n
        Returns: euler_angles (numpy.ndarray): 欧拉角 [Yaw, Pitch, Roll]。
        """
        rot_matrix = T[:3, :3]
        r = R.from_matrix(rot_matrix)
        euler_angles = r.as_euler('xyz', degrees=True)  # 'xyz' 表示XYZ欧拉角顺序
        return euler_angles
    
    def quaternionToEuler(self,w, x, y, z):
        """
        说明：将四元数 (w, x, y, z) 转换为欧拉角 (yaw, pitch, roll)，旋转顺序为 ZYX
        """
        norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
        w, x, y, z = w / norm, x / norm, y / norm, z / norm
        yaw = np.arctan2(2 * (w * z + x * y), 1 - 2 * (y**2 + z**2))
        pitch = np.arcsin(2 * (w * y - z * x))
        roll = np.arctan2(2 * (w * x + y * z), 1 - 2 * (x**2 + y**2))
        return np.array([yaw, pitch, roll])
    
    def matrixToQuat(self,rot_matrix):
        """
        说明： 将旋转矩阵转换为四元数\n   
        返回： w, x, y, z
        """
        r = R.from_matrix(rot_matrix) 
        quat = r.as_quat()     # 返回 [x, y, z, w] 格式的四元数
        quat = np.roll(quat,1) # 返回 [w, x, y, z] 格式的四元数
        return np.array(quat).astype(float)
    
    def quatToMatrix(self,w, x, y, z):
        """
        说明：(四元数)转换为旋转矩阵
        """
        norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
        w, x, y, z = w / norm, x / norm, y / norm, z / norm 
        rotation_matrix = np.array([
            [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)]
        ])
        return rotation_matrix

    def poseToMatrix(self,position, orientation): 
        """
        说明：(位置,四元数)转换为齐次变换矩阵
        """
        if isinstance(position, list):
            x, y, z = position 
        else:
            x, y, z = position.x, position.y, position.z
        if isinstance(orientation, list):
            qw, qx, qy, qz = orientation  
        else:
            qw, qx, qy, qz = orientation.w, orientation.x, orientation.y, orientation.z
        rotation_matrix = self.quatToMatrix(qw, qx, qy, qz)
        transformation_matrix = np.eye(4)
        transformation_matrix[:3, :3] = rotation_matrix
        transformation_matrix[:3, 3] = [x, y, z]
        return transformation_matrix
    def matrixToPoseStampedPub(self, matrix,headerTimers):
        """
        说明：齐次变换矩阵转换为位姿信息\n
        参数： matrix:齐次变换矩阵\n
        参数： headerTimers:时间戳
        """
        pose = PoseStamped()
        pose.header.stamp = headerTimers
        pose.header.frame_id = "base"  # 设基坐标系frame为"base"
        pose.pose.position.x = matrix[0, 3]
        pose.pose.position.y = matrix[1, 3]
        pose.pose.position.z = matrix[2, 3]
        quat = self.matrixToQuat(matrix[:3, :3])
        pose.pose.orientation.w = quat[0]
        pose.pose.orientation.x = quat[1]
        pose.pose.orientation.y = quat[2]
        pose.pose.orientation.z = quat[3]
        return pose
    
