import numpy as np

def generate_cycloid_dxf(filename, ratio, R, r_p, e, N_in, R_in, r_in_pin, r_center, num_points=2000):
    Z = ratio       # ディスクの歯数（減速比）
    N = Z + 1       # 外輪ピンの数
    
    phi = np.linspace(0, 2 * np.pi, num_points)
    
    # 1. 外輪ピン中心がディスクから見て描く軌跡（エピトロコイド）
    xc = R * np.cos(phi) - e * np.cos(N * phi)
    yc = R * np.sin(phi) - e * np.sin(N * phi)
    
    # 2. 軌跡の微分（法線ベクトルを求めるため）
    dxc = -R * np.sin(phi) + e * N * np.sin(N * phi)
    dyc =  R * np.cos(phi) - e * N * np.cos(N * phi)
    
    # 3. 法線ベクトルの計算
    norm = np.hypot(dxc, dyc)
    nx = dyc / norm
    ny = -dxc / norm
    
    # 4. ピンの半径(r_p)分だけ法線方向（内側）にオフセットして実体形状にする
    X = xc - r_p * nx
    Y = yc - r_p * ny
    
    # 出力ピン用穴の半径 (ピン半径 + 偏心量)
    r_hole = r_in_pin + e

    # DXF(R12互換形式)への書き出し
    with open(filename, 'w') as f:
        f.write("  0\nSECTION\n  2\nHEADER\n  0\nENDSEC\n")
        f.write("  0\nSECTION\n  2\nTABLES\n  0\nENDSEC\n")
        f.write("  0\nSECTION\n  2\nBLOCKS\n  0\nENDSEC\n")
        f.write("  0\nSECTION\n  2\nENTITIES\n")
        
        # 外形ポリライン
        f.write("  0\nPOLYLINE\n  8\n0\n 66\n1\n 70\n1\n") 
        for x, y in zip(X, Y):
            f.write("  0\nVERTEX\n  8\n0\n")
            f.write(f" 10\n{x:.6f}\n 20\n{y:.6f}\n 30\n0.0\n")
        f.write("  0\nSEQEND\n  8\n0\n")
        
        # 中心穴
        if r_center > 0:
            f.write("  0\nCIRCLE\n  8\n0\n")
            f.write(f" 10\n0.0\n 20\n0.0\n 30\n0.0\n")
            f.write(f" 40\n{r_center:.6f}\n")

        # 出力ピン用穴
        if N_in > 0 and R_in > 0:
            for i in range(N_in):
                theta = 2 * np.pi * i / N_in
                cx = R_in * np.cos(theta)
                cy = R_in * np.sin(theta)
                f.write("  0\nCIRCLE\n  8\n0\n")
                f.write(f" 10\n{cx:.6f}\n 20\n{cy:.6f}\n 30\n0.0\n")
                f.write(f" 40\n{r_hole:.6f}\n")

        f.write("  0\nENDSEC\n  0\nEOF\n")
    print(f"{filename} を作成しました。")

if __name__ == "__main__":
    # --- パラメータ設定 ---
    RATIO = 11      # 減速比 (ディスク歯数)
    e = 1.5         # 偏心量 (mm)
    R = 30.0        # 外輪ピンの配置円半径 (mm)
    r_p = 2.0       # 外輪ピンの半径 (mm)
    N_in = 6        # 出力ピンの数 (個)
    R_in = 20.0     # 出力ピンの配置円半径 (mm)
    r_in_pin = 4.0  # 出力ピンの半径 (mm)
    r_center = 5.0 # 中心穴の半径 (mm)

    generate_cycloid_dxf("cycloid.dxf", RATIO, R, r_p, e, N_in, R_in, r_in_pin, r_center)