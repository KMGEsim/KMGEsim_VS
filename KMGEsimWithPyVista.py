from tkinter import *
import tkinter
from tkinter import filedialog
import csv
import time
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import multiprocessing
import os
import re
from tkinter import ttk
from colour import Color
import matplotlib
from matplotlib import cm
import seaborn as sb
sb.set_theme()

class Example(Frame):


    def __init__(self, parent):

        Frame.__init__(self, parent)   
        self.parent = parent 
        self.__Unit__()


    def __Unit__(self):
        
        self.OveralDf = pd.DataFrame()
        self.InjectorDf = {}
        self.D3MeshDf = {}
        self.three_d_names = []
        self.ProducerDf = pd.DataFrame()
        self.pack(fill=BOTH, expand=1)
        self.menubar = Menu(self.parent)
        self.parent.config(menu=self.menubar)
        self.fileMenu = Menu(self.menubar,tearoff=0)
        self.fileMenu.add_command(label="Open", command=self.onOpen)
        self.fileMenu.add_command(label="Clear", command=self.clear)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.summaryMenu=Menu(self.menubar, tearoff=0)
        self.submenu = Menu(self.summaryMenu, tearoff=0)
        self.summaryMenu.add_cascade(label='Well', menu=self.submenu)
        self.summaryMenu.add_command(label='Overall', command=self.overalOpen)
        self.menubar.add_cascade(label='Summary', menu=self.summaryMenu)
        self.p = pv.Plotter()
        self.solutionMenu=Menu(self.menubar, tearoff=0) 
        self.menubar.add_cascade(label='Solution', menu=self.solutionMenu)
        self.m = 1


    def onOpen(self):

        list_ = self.grid_slaves()
        for l in list_:
            l.destroy()
        self.__Unit__()
        ftypes = [('Overal files', '*.OVERAL'), ('All files', '*')]
        dlg = filedialog.Open(self, filetypes=ftypes)
        fl = dlg.show()
        if fl != '':
            print('----------------------Start reading!')
            self.readFile(fl, os.path.dirname(fl))


    def solutionOpen(self, item):

        self.summary(f'{item}')


    def clear(self):

        lists = self.grid_slaves()
        for lis in lists:
            lis.destroy()
        self.__Unit__()

    def overalOpen(self):

        self.drawGrap(self.OveralDf)

    def injectorOpen(self, item):

        lists = self.grid_slaves()
        for lis in lists:
            lis.destroy()
        self.drawGrap(self.InjectorDf[f'{item}'][0])

    def overal_read(self, path):
        try:
            # read overal file
            file = open(path, "r")
            data_overal = file.readlines()
            startIndex = data_overal.index("   LIST OF VARIABLES ARE : \n")
            endIndex = [data_overal.index(a) for a in data_overal if re.findall(r'   TOTAL NO. OF VARIABLES IS =  [\d]+', a)][0]
            numberOfVariable = int(re.findall(r'([\d]+)', data_overal[endIndex])[0])
            headers = []
            for i in range(startIndex+2,endIndex):
                if data_overal[i].count(':') == 0:
                    headers += [a.split('-')[1].strip() for a in data_overal[i].strip().split(',')]
                else:
                    if data_overal[i].__contains__('FOR EACH PHASE'):
                        (a,b) = re.findall(r'([\d]+)-([\d]+)', data_overal[i].strip())[0]
                        count = int(b) - int(a) + 2
                        word = re.findall(r': (.+) FOR EACH PHASE', data_overal[i].strip())[0]
                        headers += [f'{word}_{reti}' for reti in range(1, count)]
                    else:
                        (a,b) = re.findall(r'([\d]+)-[ ]?([\d]+)', data_overal[i].strip())[0]
                        count = int(b) - int(a) + 1
                        if count == len(data_overal[i].strip().split(':')[1].strip().split(',')):
                            words = data_overal[i].strip().split(':')[1].strip().split(',')
                            headers += [c.strip() for c in words]
                        else:
                            words = data_overal[i].strip().split(':')[1].strip().split(',')
                            headers += [reti.strip() for word in words for reti in word.split('AND') ]

            headers = [i.strip().replace(' ', '_') for i in headers]
            headers = [i.replace('.', '') for i in headers]
            print('----------------------Overall reading done!')
            with open('overall.csv', 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                # write the header
                writer.writerow(headers)
                # write the data
                shag = endIndex-startIndex-2
                for i in range(endIndex+3, len(data_overal), shag):
                    my_dt = []
                    for j in range(shag):
                        my_dt += data_overal[i+j].strip().split(',')[:-1]
                    writer.writerow(my_dt)
        except Exception as ex:
            print(ex)


    def injector_read(self, path):

        try:
            # read well block inector and producer
            file = open(path, "r")
            data_well = file.readlines()
            name = [re.findall(r'HISTORY DATA FOR WELL:[ ]+ID[ ]+=.+=[ ]+(.+)', a) for a in data_well if re.findall(r'HISTORY DATA FOR WELL:[ ]+ID[ ]+=.+=[ ]+(.+)', a)][0][0].strip()
            startIndex = data_well.index("   LIST OF VARIABLES ARE : \n")
            endIndex = [data_well.index(a) for a in data_well if re.findall(r'   TOTAL NO. OF VARIABLES FOR A.+ IS =[ ]+[\d]+', a)][0]
            numberOfVariable = int(re.findall(r'([\d]+)', data_well[endIndex])[0])
            headers=[]
            for i in range(startIndex+2,endIndex):
                if data_well[i].count(':') == 0:
                    headers += [a.split('-')[1].strip() for a in data_well[i].strip().split(',')]
                else:
                    if data_well[i].__contains__('FOR EACH WELLBLOCK'):
                        (a, b) = re.findall(r'([\d]+)-[ ]+([\d]+)[ ]+:', data_well[i].strip())[0]
                        count = int(b) - int(a) + 2
                        if (int(a) - int(b)) == 0:
                            words = data_well[i].strip().split(':')[1].strip()
                            headers += [words]
                        else:
                            word = re.findall(r': (.+) FOR EACH WELLBLOCK', data_well[i].strip())[0]
                            headers += [f'{word}_{reti}' for reti in range(1, count)]
                    else:
                        (a, b) = re.findall(r'([\d]+)-[ ]+([\d]+)', data_well[i].strip())[0]
                        count = int(b) - int(a) + 2
                        if (int(a) - int(b)) == 0:
                            words = data_well[i].strip().split(':')[1].strip()
                            headers += [words]
                        else:
                            word = re.findall(r': (.+)', data_well[i].strip())[0]
                            headers += [f'{word}_{reti}' for reti in range(1, count)]
            headers = [i.strip().replace(' ', '_') for i in headers]
            cols = 0
            hedcount = 0
            for i in range(endIndex + 3, len(data_well)):
                row = data_well[i].strip().split(', ')
                cols += 1
                hedcount += len(row)
                if hedcount == len(headers):
                    break
            print(f'----------------------Well block reading is {name} done!')
            with open(f'{name}.csv', 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                # write the header
                writer.writerow(headers)
                # write the data
                for i in range(endIndex + 3, len(data_well), cols):
                    my_dt= []
                    for j in range(cols):
                        my_dt += data_well[i+j].strip().split(', ')
                    writer.writerow(my_dt)
            return [name]
        except Exception as ex:
            print(ex)
            return []


    def read_mesh_concp(self, fname, dirname):

        try:
            # read MESH file
            file_mesh = open(f'{dirname}/{fname}.MESH', "r")
            data_mesh = file_mesh.readlines()
            NX, NY, NZ = re.findall(r'NX =[ ]+([\d]+)[ ]+NY =[ ]+([\d]+)[ ]+NZ =[ ]+([\d]+)', data_mesh[0])[0]
            NX, NY, NZ = int(NX), int(NY), int(NZ)
            beginIndx = [data_mesh.index(i) for i in data_mesh if re.findall(r'XSCALE, YSCALE, ZSCALE IN FT', i)][0]
            endIndx = [data_mesh.index(i) for i in data_mesh if re.findall(r'X-CORD', i)][0]
            a = [float(el) for el in ' '.join([i.strip() for i in data_mesh[beginIndx+1:endIndx]]).split()]
            xscale, yscale, zscale = a[:NX], a[NX:NX+NY], a[NY+NY:NZ+NX+NY]
            xcord, ycord, welname, symbol = [], [], [], []
            for i in range(endIndx+1,len(data_mesh)):
                xcord.append(float(data_mesh[i].strip().split(',')[0]))
                ycord.append(float(data_mesh[i].strip().split(',')[1]))
                welname.append(data_mesh[i].strip().split(',')[2])
                symbol.append(data_mesh[i].strip().split(',')[3])
            return NX, NY, NZ, xscale, yscale, zscale, xcord, ycord, welname, symbol
        except Exception as ex:
            print(ex)


    def mesh_3d_read(self, dirname, three_d):

        try:
            # read 3D data files
            path = f"{dirname}/{three_d}"
            file = open(path, "r")
            data = file.readlines()
            NX, NY, NZ = re.findall(r'NX =[ ]+([\d]+)[ ]+NY =[ ]+([\d]+)[ ]+NZ =[ ]+([\d]+)', data[4])[0]
            NX, NY, NZ = int(NX), int(NY), int(NZ)

            times = [data.index(i) for i in data if re.findall(r'^TIME', i)]
            headers =['DAYS', 'PV']
            headers += [re.findall(r'(.+)IN LAYER', data[i].strip())[0].strip().replace(' ', '_') for i in range(times[0],times[1]) if re.findall(r'.+IN LAYER[ ]+[1]$', data[i])]

            comp_aq = pd.DataFrame([], columns = headers)

            for el in range(2,len(headers)):
                    self.D3MeshDf[headers[el]] = []

            for data_id in times:
                time_pv = data[data_id].strip().split()
                days, pv = [float(time_pv[el_id+1]) for el_id in range(len(time_pv)) if time_pv[el_id]=='=']
                row = {"DAYS":days, "PV":pv}
                for el in range(2,len(headers)):
                    row[headers[el]] = []
                for z in range(1,NZ+1):
                    count = 1
                    for j in range(data_id+1,data_id+(len(headers)-2)*(NY+1), NY+1):
                        my_dt = []
                        count += 1
                        for i in range(1, NY+1):
                            my_dt += [float(k) for k in data[i+j].strip().split()]
                        row[headers[count]].append(my_dt)
                for el in range(2,len(headers)):
                    self.D3MeshDf[headers[el]].append(row[headers[el]])

                comp_aq = comp_aq.append(row, ignore_index=True)
            #comp_aq.to_csv(f"{three_d}.csv")
            print(f'----------------------{three_d} is reading!')
            self.three_d_names += headers[2:]
        except Exception as ex:
            print(ex)
        return ''

    def readFile(self, fullpath, dirname):
        
        f_name = fullpath.split('/')[-1].split('.')[0]
        self.overal_read(fullpath)
        files_list = [i for i in os.listdir(dirname) if i.__contains__(f'{f_name}')]
        output_names = []
        for hists in [nn for nn in files_list if nn.__contains__('.HIST')]:
            output_names += self.injector_read(f"{dirname}/{hists}")
        for item in output_names:
            self.InjectorDf[f'{item}'] = [pd.read_csv(f'{item}.csv')]
            self.submenu.add_command(label=f'{item}',
                                     command=lambda arg=f'{item}':
                                     self.injectorOpen(arg))
        self.OveralDf = pd.read_csv('overall.csv')
        #three_d_names = []
        three_d = []
        for i in ['.ALKP', '.COMP', '.CONCP', '.PRESP', 
                  '.PERM', '.RPERM', '.SALT', '.SATP', '.TRAP', '.VISC']:
            for nn in files_list:
                if nn.__contains__(i):
                    three_d += [nn]
        start = time.time()
        for n in three_d:
            self.mesh_3d_read(dirname, n)
            #time.sleep(2)
        print(f'It took {(time.time() - start)}')
        print('----------------------Reading is done!!!')
        self.solutionMenu.add_command(label="3D",
                                      command=lambda arg=self.three_d_names,
                                      f_n=f_name,
                                      dirname=dirname:
                                      self.threeDOpen(arg, f_n, dirname))
        return ' '


    def drawGrap(self, df=pd.DataFrame()):
        # draw 3d graf
        headers = [i for i in df.keys()]
        head_list = StringVar(value=headers)
        time = StringVar()
        sentmsg = StringVar()
        statusmsg = StringVar()
        f = Figure(figsize=(6, 5), dpi=100)
        f_plot = f.add_subplot(111)
        def showGrid(*args):
            idxs = lbox.curselection()
            f_plot.clear()
            if len(idxs) == 1:
                idx = int(idxs[0])
                ox = headers[idx]
                oy = time.get()
                f_plot.clear()
                if oy == 'Days':
                    f_plot.plot(df['DAYS'], df[f'{ox}'])
                    f_plot.set(xlabel='DAYS', ylabel=f'{ox}')
                else:
                    f_plot.plot(df['PV'], df[f'{ox}'])
                    f_plot.set(xlabel='PV', ylabel=f'{ox}')
                canvs.draw()
                statusmsg.set("The graph  of %s" % (ox))
            sentmsg.set('')

        c = ttk.Frame(self, padding=(5, 5, 12, 0))
        c.grid(column=0, row=0, sticky=(N, W, E, S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        lbox = Listbox(c, listvariable=head_list, height=5)
        lbl = ttk.Label(c, text="Choose Y (Default: days):")
        g1 = ttk.Radiobutton(c, text='Days', variable=time, value='Days')
        g2 = ttk.Radiobutton(c, text='PV', variable=time, value='PV')
        sentlbl = ttk.Label(c, textvariable=sentmsg, anchor='center')
        status = ttk.Label(c, textvariable=statusmsg, anchor=W)
        lbox.grid(column=0, row=0, rowspan=6, sticky=(N, S, E, W))
        lbl.grid(column=1, row=0, padx=10, pady=5)
        g1.grid(column=1, row=1, sticky=W, padx=20)
        g2.grid(column=1, row=2, sticky=W, padx=20)
        sentlbl.grid(column=1, row=5, columnspan=2, sticky=N, pady=5, padx=5)
        status.grid(column=0, row=6, columnspan=2, sticky=(W, E))
        c.grid_columnconfigure(0, weight=1)
        c.grid_rowconfigure(5, weight=1)
        lbox.bind('<<ListboxSelect>>', showGrid)
        for i in range(0, len(headers), 2):
            lbox.itemconfigure(i, background='#f0f0ff')
        canvs = FigureCanvasTkAgg(f, self)
        canvs.get_tk_widget().grid(column=0, row=1)
        time.set('Days')
        sentmsg.set('')
        statusmsg.set('')
        lbox.selection_set(0)
        showGrid()


    def threeDOpen(self, names, f_n, dirname):

        if os.path.exists(f'{dirname}/{f_n}.WARN'):
            warn_file = open(f'{dirname}/{f_n}.WARN', "r")
            warn_data = warn_file.readlines()
            warn = sorted([int(re.findall(r'NOTE: THE CELL #[ ]+(\d+)', a)[0])
                           for a in warn_data
                           if re.findall(r'NOTE: THE CELL #[ ]+(\d+)', a)])

        def draw_cube(datas, row_name, NX, NY, NZ, xscale, yscale, zscale, xcord, ycord, welname, symbol):

            try:
                pv.global_theme.background = "black"
                datas = np.array(datas)
                ni, nj, nk = NX, NY, NZ
                si, sj, sk = 2 * xscale[0], 2 * yscale[0], 2 * zscale[0]

                na = []
                z = 2 * zscale[0] + zscale[len(zscale)-1]
                for i in range(len(xcord)):
                    na.append([xcord[i], ycord[i], z])
                poly = pv.PolyData(np.array(na))
                poly["My Labels"] = welname
                xcorn = np.arange(0, (ni+1)*si, si)
                xcorn = np.repeat(xcorn, 2)
                xcorn = xcorn[1:-1]
                xcorn = np.tile(xcorn, 4*nj*nk)

                ycorn = np.arange(0, (nj+1)*sj, sj)
                ycorn = np.repeat(ycorn, 2)
                ycorn = ycorn[1:-1]
                ycorn = np.tile(ycorn, (2*ni, 2*nk))
                ycorn = np.transpose(ycorn)
                ycorn = ycorn.flatten()

                zcorn = np.arange(0, (nk+1)*sk, sk)
                zcorn = np.repeat(zcorn, 2)
                zcorn = zcorn[1:-1]
                zcorn = np.repeat(zcorn, (4*ni*nj))

                fetch = lambda index: datas[index].flatten()

                corners = np.stack((xcorn, ycorn, zcorn))
                corners = corners.transpose()
                dims = np.asarray((ni, nj, nk))+1
                self.p.add_point_labels(poly, "My Labels", point_size=15, font_size=20, text_color="red")

                
                def create_grid(value):

                    grid = pv.ExplicitStructuredGrid(dims, corners)
                    grid['values'] = fetch(int(value))
                    grid.compute_connectivity()
                    self.p.add_mesh(grid, show_edges=True, cmap="rainbow", clim=[np.min(datas), np.max(datas)])
                    return

                max_value = len(datas)-1
                actor = self.p.add_slider_widget(create_grid, [0, max_value], title='Time')
                cpos = self.p.show()
            except Exception as ex:
                print(ex)


        def show3d(*args):
            idxs = lbox.curselection()
            if len(idxs) == 1:
                idx = int(idxs[0])
                row_name = headers[idx]
                datas = self.D3MeshDf[row_name]
                draw_cube(datas, row_name, NX, NY, NZ,\
                          xscale, yscale, zscale, xcord,\
                          ycord, welname, symbol)
            sentmsg.set('')

        try:
            headers = names
            head_list = StringVar(value=headers)
            NX, NY, NZ, xscale, yscale, zscale, xcord,\
                ycord, welname, symbol = self.read_mesh_concp(f_n, dirname)
            time = StringVar()
            sentmsg = StringVar()
            statusmsg = StringVar()

            c = ttk.Frame(self, padding=(5, 5, 12, 0))
            c.grid(column=0, row=0, sticky=(N, W, E, S))

            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            lbox = Listbox(c, listvariable=head_list, height=5)

            sentlbl = ttk.Label(c, textvariable=sentmsg, anchor='center')
            status = ttk.Label(c, textvariable=statusmsg, anchor=W)

            lbox.grid(column=0, row=0, rowspan=6, sticky=(N, S, E, W))

            sentlbl.grid(column=1, row=5, columnspan=2, sticky=N, pady=5, padx=5)
            status.grid(column=0, row=6, columnspan=2, sticky=(W, E))

            c.grid_columnconfigure(0, weight=1)
            c.grid_rowconfigure(5, weight=1)

            lbox.bind('<<ListboxSelect>>', show3d)
            for i in range(0, len(headers), 2):
                lbox.itemconfigure(i, background='#f0f0ff')

            time.set('Days')
            sentmsg.set('')
            statusmsg.set('')
            lbox.selection_set(0)
        except Exception as ex:
            print(ex)


def main():
    
    root = Tk()
    root.title('KMGEsim')
    ex = Example(root)
    root.geometry("650x700")
    root.iconbitmap('KMGEsim.ico')
    root.mainloop()


if __name__ == '__main__':
    main()
