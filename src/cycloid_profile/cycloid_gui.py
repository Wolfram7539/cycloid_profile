import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CycloidGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("サイクロイド減速機ジェネレーター")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # --- 変数の定義と初期値 ---
        self.var_ratio = tk.IntVar(value=11)
        self.var_e = tk.DoubleVar(value=1.5)
        self.var_R = tk.DoubleVar(value=45.0)
        self.var_rp = tk.DoubleVar(value=4.0)
        self.var_Nin = tk.IntVar(value=6)
        self.var_Rin = tk.DoubleVar(value=25.0)
        self.var_rin_pin = tk.DoubleVar(value=5.0)
        self.var_r_center = tk.DoubleVar(value=10.0)

        # --- GUI構築 ---
        self.create_widgets()
        self.update_plot()

    def create_widgets(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左側：パラメータ設定パネル
        left_frame = ttk.LabelFrame(main_frame, text="設計パラメータ", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # スピンボックス（数値入力欄）を作成するヘルパー関数
        def add_spinbox(parent, label, var, from_, to, increment):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            spin = ttk.Spinbox(frame, textvariable=var, from_=from_, to=to, increment=increment, width=10, command=self.update_plot)
            spin.pack(side=tk.RIGHT)
            # 値を手入力してEnterを押した時や、フォーカスが外れた時にも更新
            spin.bind('<Return>', lambda e: self.update_plot())
            spin.bind('<FocusOut>', lambda e: self.update_plot())

        add_spinbox(left_frame, "減速比 [歯数] (Z):", self.var_ratio, 5, 100, 1)
        add_spinbox(left_frame, "偏心量 e (mm):", self.var_e, 0.1, 10.0, 0.1)
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        add_spinbox(left_frame, "外輪ピン配置円半径 R (mm):", self.var_R, 10.0, 200.0, 1.0)
        add_spinbox(left_frame, "外輪ピン半径 r_p (mm):", self.var_rp, 1.0, 20.0, 0.5)
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        add_spinbox(left_frame, "出力ピン数 N_in:", self.var_Nin, 3, 20, 1)
        add_spinbox(left_frame, "出力ピン配置円半径 R_in (mm):", self.var_Rin, 5.0, 150.0, 1.0)
        add_spinbox(left_frame, "出力ピン半径 r_in_pin (mm):", self.var_rin_pin, 1.0, 20.0, 0.5)
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        add_spinbox(left_frame, "中心軸穴半径 r_center (mm):", self.var_r_center, 0.0, 50.0, 1.0)

        # 更新ボタン
        ttk.Button(left_frame, text="プレビュー更新", command=self.update_plot).pack(fill=tk.X, pady=(15, 5))
        
        # DXFエクスポートボタン
        ttk.Button(left_frame, text="DXFとして保存...", command=self.export_dxf).pack(fill=tk.X, pady=5)

        # 右側：プレビューパネル (MatplotlibのキャンバスをTkinterに埋め込む)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_cycloid_profile(self):
        """パラメータからサイクロイド曲線の座標(X, Y)を計算する"""
        try:
            Z = self.var_ratio.get()
            e = self.var_e.get()
            R = self.var_R.get()
            r_p = self.var_rp.get()
            
            N = Z + 1
            phi = np.linspace(0, 2 * np.pi, 2000)
            
            # エピトロコイド軌跡
            xc = R * np.cos(phi) - e * np.cos(N * phi)
            yc = R * np.sin(phi) - e * np.sin(N * phi)
            
            # 軌跡の微分
            dxc = -R * np.sin(phi) + e * N * np.sin(N * phi)
            dyc =  R * np.cos(phi) - e * N * np.cos(N * phi)
            
            # 法線ベクトルの計算
            norm = np.hypot(dxc, dyc)
            norm[norm == 0] = 1e-10 # ゼロ割回避
            nx = dyc / norm
            ny = -dxc / norm
            
            # オフセット処理
            X = xc - r_p * nx
            Y = yc - r_p * ny
            
            return X, Y
        except Exception:
            return None, None

    def update_plot(self):
        """プレビューの再描画"""
        self.ax.clear()
        
        try:
            Z = self.var_ratio.get()
            e = self.var_e.get()
            R = self.var_R.get()
            r_p = self.var_rp.get()
            N_in = self.var_Nin.get()
            R_in = self.var_Rin.get()
            r_in_pin = self.var_rin_pin.get()
            r_center = self.var_r_center.get()
            
            # ディスク外形描画 (青線)
            X, Y = self.get_cycloid_profile()
            if X is not None:
                self.ax.plot(X, Y, 'b-', label='ディスク外形', linewidth=1.5)
            
            # 外輪ピンの描画 (グレー破線)
            N = Z + 1
            pin_angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
            for angle in pin_angles:
                cx = R * np.cos(angle)
                cy = R * np.sin(angle)
                circle = plt.Circle((cx, cy), r_p, color='gray', fill=False, linestyle='--')
                self.ax.add_patch(circle)
            
            # 出力ピン用穴の描画 (赤線)
            r_hole = r_in_pin + e
            if N_in > 0 and R_in > 0:
                hole_angles = np.linspace(0, 2 * np.pi, N_in, endpoint=False)
                for angle in hole_angles:
                    cx = R_in * np.cos(angle)
                    cy = R_in * np.sin(angle)
                    # ディスクに空ける穴
                    hole_circle = plt.Circle((cx, cy), r_hole, color='r', fill=False, linewidth=1.5)
                    self.ax.add_patch(hole_circle)
                    # 比較用の出力ピン自体 (緑点線)
                    pin_circle = plt.Circle((cx, cy), r_in_pin, color='green', fill=False, linestyle=':')
                    self.ax.add_patch(pin_circle)
            
            # 中心穴の描画 (黒線)
            if r_center > 0:
                center_circle = plt.Circle((0, 0), r_center, color='black', fill=False, linewidth=1.5)
                self.ax.add_patch(center_circle)

            # グラフの見た目調整
            self.ax.set_aspect('equal')
            self.ax.grid(True, linestyle=':', alpha=0.6)
            
            # 余白を自動調整
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as ex:
            print("Plot error:", ex)

    def export_dxf(self):
        """R12互換形式でDXFファイルを出力"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF Files", "*.dxf")],
            title="DXFファイルの保存先を選択"
        )
        if not file_path:
            return
            
        try:
            e = self.var_e.get()
            N_in = self.var_Nin.get()
            R_in = self.var_Rin.get()
            r_in_pin = self.var_rin_pin.get()
            r_center = self.var_r_center.get()
            
            X, Y = self.get_cycloid_profile()
            if X is None:
                return
                
            r_hole = r_in_pin + e

            with open(file_path, 'w') as f:
                f.write("  0\nSECTION\n  2\nHEADER\n  0\nENDSEC\n")
                f.write("  0\nSECTION\n  2\nTABLES\n  0\nENDSEC\n")
                f.write("  0\nSECTION\n  2\nBLOCKS\n  0\nENDSEC\n")
                f.write("  0\nSECTION\n  2\nENTITIES\n")
                
                # 外形線 (POLYLINE)
                f.write("  0\nPOLYLINE\n  8\n0\n 66\n1\n 70\n1\n") 
                for x, y in zip(X, Y):
                    f.write("  0\nVERTEX\n  8\n0\n")
                    f.write(f" 10\n{x:.6f}\n 20\n{y:.6f}\n 30\n0.0\n")
                f.write("  0\nSEQEND\n  8\n0\n")
                
                # 中心穴 (CIRCLE)
                if r_center > 0:
                    f.write("  0\nCIRCLE\n  8\n0\n")
                    f.write(f" 10\n0.0\n 20\n0.0\n 30\n0.0\n")
                    f.write(f" 40\n{r_center:.6f}\n")

                # 出力ピン用穴 (CIRCLE)
                if N_in > 0 and R_in > 0:
                    for i in range(N_in):
                        theta = 2 * np.pi * i / N_in
                        cx = R_in * np.cos(theta)
                        cy = R_in * np.sin(theta)
                        f.write("  0\nCIRCLE\n  8\n0\n")
                        f.write(f" 10\n{cx:.6f}\n 20\n{cy:.6f}\n 30\n0.0\n")
                        f.write(f" 40\n{r_hole:.6f}\n")

                f.write("  0\nENDSEC\n  0\nEOF\n")
            
            messagebox.showinfo("保存完了", f"DXFファイルを作成しました。\n{file_path}")
        except Exception as ex:
            messagebox.showerror("エラー", f"DXFの保存中にエラーが発生しました。\n{ex}")

    def on_closing(self):
        """ウィンドウを閉じるときにプログラムを完全に終了する"""
        plt.close('all')      # Matplotlibのバックグラウンドプロセスを終了
        self.root.quit()      # Tkinterのメインループを終了
        self.root.destroy()   # ウィンドウリソースを破棄
        import sys
        sys.exit(0)

def main():
    root = tk.Tk()
    app = CycloidGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()