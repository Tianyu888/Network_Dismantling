import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import sys
import ui1
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import matplotlib as mpl
from modify import *
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.artist
from PIL import Image
from matplotlib.backend_bases import MouseButton
import testSynthetic
import sys,os
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
from FINDER import FINDER
from tqdm import tqdm

class MatplotlibWidget(QWidget):

    # Matplotlib Widget which displaying the network
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        # Initialize figure attributes
        # plt.style.use('seaborn-deep')
        self.figure = Figure(dpi=80)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)

        # self.axis.set_xticks(range(0, 11, 1))
        # self.axis.set_yticks(range(0, 11, 1))
        # self.axis.xaxis.set_visible(False)
        # self.axis.yaxis.set_visible(False)

        # Limit the upper and lower bound of x and y values


        # Implement the canvas to the layout
        self.layoutvertical = QVBoxLayout(self)
        self.layoutvertical.addWidget(self.canvas)

    def set_limit(self):
        self.axis.set_xlim([-0.2, 10.2])
        self.axis.set_ylim([-0.2, 10.2])

# Main class for the application
class MainWidget(QWidget, ui1.Ui_Form):
    lock = None

    def __init__(self):
        super(MainWidget, self).__init__()
        self.setupUi(self)
        self.setFixedSize(1020,800)
        self.score_list = list()
        self.init_widget()
        self.init_bartool()
        self.b = self.matplotlibwidget.axis.scatter([], [], color='#f1595f', marker='o', s=50, zorder=2)
        self.b_1 = self.matplotlibwidget_1.axis.scatter([], [], color='#f1595f', marker='o', s=50, zorder=2)
        self.ModeParam.setCurrentIndex(1)  # set default page
        self.NetworkParam1.setCurrentIndex(0) # set default Network Para Page
        self.Attack_method.setCurrentIndex(0)  # set default attack method for ER network
        self.AttackParameter.setCurrentIndex(0) # set default attack parameter
        self.NetworkcomboBox1.activated[int].connect(
            self.NetworkParam1.setCurrentIndex)  # combobox: change network mode
        self.Attack_method.activated[int].connect(
            self.AttackParameter.setCurrentIndex)  # combobox: change network mode
        # Draw button connected to four given networks
        self.Draw_Network.clicked.connect(self.choose_and_draw)
        # Main page Start! button connected to the mode selected in the combobox upwards
        self.ModeChange.clicked.connect(self.modechoose)
        self.Back.clicked.connect(self.back)  # Back to the Main page from Attack mode
        self.Back_2.clicked.connect(self.back)  # Back to the Main page from Defend mode
        self.YourNetwork.clicked.connect(self.draw_custom_result)  # Show network with modification by custom
        self.Start.clicked.connect(self.start_attack)  # Attack by the method chosen
        self.Confirm.clicked.connect(self.draw_custom_result)  # Confirm custom attack
        self.Confirm_2.clicked.connect(self.draw_custom_result_2)  # Confirm custom attack
        self.ShowAnswer.clicked.connect(self.GCC_or_SCC)  # Find the best result by algo (attack)
        self.Original.clicked.connect(self.draw_OriginalNetwork)  # show the original network before attack/defend
        self.Original_2.clicked.connect(self.draw_OriginalNetwork)  # show the original network before attack/defend
        self.Defend_Network.clicked.connect(self.draw_defend_network)  # Draw the defending network
        self.Start_2.clicked.connect(self.defend_start) # Start drawing edges
        self.ShowResult.clicked.connect(self.Show_Result)  # Find the best result by algo (defend)
        self.Start_2.clicked.connect(self.defend_start)
        # self.matplotlibwidget_1.canvas.mpl_connect('button_press_event', self.add_or_remove_point)
        self.G = nx.Graph()  #Main Graph
        self.ResultNetwork = None
        self.CustomNetwork = None
        self.directed = None
        self.poly = None
        self.YourScore = 0
        self.ResultScore = 0
        self.bombwidth, self.bomblength = 2, 2 #default bomb size
        self.start, self.moved = True, False
        self.Start.setEnabled(False)
        self.Confirm.setEnabled(False)
        self.Original.setEnabled(False)
        self.YourNetwork.setEnabled(False)
        self.ShowAnswer.setEnabled(False)
        self.Confirm_2.setEnabled(False)
        self.ShowResult.setEnabled(False)
        self.Original_2.setEnabled(False)
        self.canvas = 0
        self.colored, self.moved = False, False
        self.attack_method = 0
        self.G_original = None
        self.trashbin = None
        self.cache = list()
        self.clickconnect = None
        self.cidpress, self.cidmotion, self.cidrelease, self.colorid, self.hoverconnect = None, None, None, None, None
        self.annot = self.matplotlibwidget.axis.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                                                     bbox=dict(boxstyle="round", fc="w"),
                                                     arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

    def init_widget(self):
        # Attack Mode
        self.matplotlibwidget = MatplotlibWidget() # Initialize the main matplotlib widget
        self.layoutvertical = QVBoxLayout(self.widget) # Initialize the layout widget
        self.layoutvertical.addWidget(self.matplotlibwidget) # Attach canvas to the vertical layout
        self.matplotlibwidget.figure.subplots_adjust(0, 0, 1, 1) # Adjust the canvas size
        self.matplotlibwidget.set_limit()
        # Attack log
        self.matplotlibwidget_log = MatplotlibWidget()  # Initialize the main matplotlib widget
        self.layoutvertical_log = QVBoxLayout(self.widget_3)  # Initialize the layout widget
        self.layoutvertical_log.addWidget(self.matplotlibwidget_log)  # Attach canvas to the vertical layout
        self.matplotlibwidget_log.figure.subplots_adjust(0.1, 0.1, 0.95, 0.95)  # Adjust the canvas size
        # FINDER log
        self.matplotlibwidget_FINDER = MatplotlibWidget()  # Initialize the main matplotlib widget
        self.layoutvertical_FINDER = QVBoxLayout(self.widget_4)  # Initialize the layout widget
        self.layoutvertical_FINDER.addWidget(self.matplotlibwidget_FINDER)  # Attach canvas to the vertical layout
        self.matplotlibwidget_FINDER.figure.subplots_adjust(0.1, 0.1, 0.95, 0.95)  # Adjust the canvas size

        # Defend Mode
        self.matplotlibwidget_1 = MatplotlibWidget() # Initialize the main matplotlib widget
        self.layoutvertical_1 = QVBoxLayout(self.widget_2) # Initialize the layout widget
        self.layoutvertical_1.addWidget(self.matplotlibwidget_1) # Attach canvas to the vertical layout
        self.matplotlibwidget_1.figure.subplots_adjust(0, 0, 1, 1) # Adjust the canvas size
        self.matplotlibwidget_1.set_limit()


    def init_bartool(self):
        # Attack Mode
        self.Drag.setStyleSheet("background-image : url(C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/drag.png);")
        # Initialize the drag button
        self.Drag.clicked.connect(self.movable)
        self.Save_Graph.clicked.connect(self.saveFileDialog) # Initialize save button
        self.Load_Graph.clicked.connect(self.openFileNameDialog) # Initialize load button
        self.Color.setStyleSheet("background-image : url(C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/color.png);")
        # Initialize color button
        self.Color.clicked.connect(self.changenodecolor)
        self.Spring_Layout.setStyleSheet("background-image : url(C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics"
                                         "/layout.png);")
        # Initialize layout button
        self.Spring_Layout.clicked.connect(self.spring_layout)

        # Defend Mode
        self.Drag_2.setStyleSheet("background-image : url(C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/drag.png);")
        # Initialize the drag button
        self.Drag_2.clicked.connect(self.movable)
        self.Color_2.setStyleSheet("background-image : url(C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/color.png);")
        # Initialize color button
        self.Color_2.clicked.connect(self.changenodecolor)
        self.Save_Graph_1.clicked.connect(self.saveFileDialog) # Initialize save button
        self.Load_Graph_1.clicked.connect(self.openFileNameDialog) # Initialize load button

    #Spring layout function using networkx integrated layout
    def spring_layout(self):
        pos_curr = self.b.get_offsets()
        self.Clear_Lines()
        changed = nx.get_node_attributes(self.G, 'pos')
        pos_spring = nx.spring_layout(self.G, center=np.array([5, 5]), scale=5)
        for i in pos_spring:
            changed[i] = (pos_spring[i][0], pos_spring[i][1])
            pos_curr[int(i)][0], pos_curr[int(i)][1] = pos_spring[i][0], pos_spring[i][1]
        nx.set_node_attributes(self.G, changed, 'pos')
        self.draw_OriginalNetwork()

    # Save File build up function
    def saveFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "GML Files (*.gml);;All Files (*);;Text Files (*.txt)",
                                                  options=options)
        if not fileName:
            return
        try:
            nx.write_gml(self.G_original, fileName)
        except Exception:
            nx.write_gml(self.G, fileName)

    # Open File and load graph build up function
    def openFileNameDialog(self):
        self.reset()
        self.bartool_switch(True)

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "GML Files (*.gml);;All Files (*);;Python Files (*.py)",
                                                  options=options)
        if not fileName:
            return
        self.G = nx.read_gml(fileName)
        self.G_original = nx.read_gml(fileName)

        mapping = dict(zip(self.G, range(0, len(self.G.nodes))))
        self.G = nx.relabel_nodes(self.G, mapping)
        self.G_original = nx.relabel_nodes(self.G_original, mapping)
        annot = nx.get_node_attributes(self.G, 'annot')

        nodes_int = dict()
        for i in self.G.nodes:
            nodes_int[i] = int(i)
            annot[i] = [annot[i]]

        G_new = nx.relabel_nodes(self.G, nodes_int)
        pos = nx.get_node_attributes(self.G, 'pos')
        pos_int_key = dict()
        for i,j in pos.items():
            pos_int_key[int(i)] = tuple(j)
        pos = pos_int_key
        nx.set_node_attributes(G_new, pos, 'pos')
        self.G = G_new
        nx.set_node_attributes(self.G, annot, 'annot')
        nx.set_node_attributes(self.G_original, annot, 'annot')
        #print(1, nx.get_node_attributes(self.G, 'annot'))
        #print(2, nx.get_node_attributes(self.G, 'pos'))
        for i in pos:
            if self.canvas == 0:
                xydata_b = self.b.get_offsets()
            elif self.canvas == 1:
                xydata_b = self.b_1.get_offsets()
            x, y = pos[i][0], pos[i][1]
            new_xydata_b = np.row_stack((xydata_b, np.array([x, y])))
            if self.canvas == 0:
                self.b.set_offsets(new_xydata_b)
            elif self.canvas == 1:
                self.b_1.set_offsets(new_xydata_b)
        self.draw_OriginalNetwork()
        self.hoverconnect = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover)  # Connect to hover highlight
        self.hoverconnect_annot = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover_annot)  # Connect to hover annotate


    # Change node color build up function
    def changenodecolor(self):
        self.default()
        self.colored = True
        if self.canvas == 0:
            self.colorid = self.matplotlibwidget.figure.canvas.mpl_connect(
                'button_press_event', self.on_press_2)
        elif self.canvas == 1:
            if self.Drag_2.isChecked():
                self.movable_disconnect()
            self.colorid = self.matplotlibwidget_1.figure.canvas.mpl_connect(
                'button_press_event', self.on_press_2)

    # disconnect changenodecolor
    def changenodecolor_disconnect(self):
        self.colored = False
        if self.canvas == 0:
            self.Color.setChecked(False)
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.colorid)
        elif self.canvas == 1:
            self.Color_2.setChecked(False)
            self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.colorid)

    # helper function for changenodecolor
    def on_press_2(self, event):
        if not event.inaxes in self.matplotlibwidget.figure.axes and \
            not event.inaxes in self.matplotlibwidget_1.figure.axes:
            return
        if self.canvas == 0:
            if self.b.contains(event)[0]:
                # print(2)
                id = self.b.contains(event)[1]['ind'][0]
                qcolor = QColorDialog.getColor()
                red, green, blue, A = qcolor.getRgb()
                facecolor = self.b.get_facecolor()
                edgecolor = self.b.get_edgecolor()
                # If the color has not been chaneged before:
                if len(facecolor) == 1:
                    L = [[i] * len(self.G.nodes) for i in facecolor][0]
                    L = np.array(L)
                    self.b._facecolors = L
                if len(edgecolor) == 1:
                    L = [[i] * len(self.G.nodes) for i in edgecolor][0]
                    L = np.array(L)
                    self.b._edgecolors = L

                self.b._facecolors[id, :] = (red / 255, green / 255, blue / 255, A / 255)
                self.b._edgecolors[id, :] = (red / 255, green / 255, blue / 255, A / 255)

        elif self.canvas == 1:
            if self.b_1.contains(event)[0]:
                id = self.b_1.contains(event)[1]['ind'][0]
                qcolor = QColorDialog.getColor()
                red, green, blue, A = qcolor.getRgb()
                facecolor = self.b_1.get_facecolor()
                edgecolor = self.b_1.get_edgecolor()
                # If the color has not been chaneged before:
                if len(facecolor) == 1:
                    L = [[i] * len(self.G.nodes) for i in facecolor][0]
                    L = np.array(L)
                    self.b_1._facecolors = L
                if len(edgecolor) == 1:
                    L = [[i] * len(self.G.nodes) for i in edgecolor][0]
                    L = np.array(L)
                    self.b_1._edgecolors = L

                self.b_1._facecolors[id, :] = (red / 255, green / 255, blue / 255, A / 255)
                self.b_1._edgecolors[id, :] = (red / 255, green / 255, blue / 255, A / 255)
        self.draw()

    # Choose and decide which canvas(depends on attack/defend mode) to be drawn
    def draw(self):
        if self.canvas == 0:
            self.matplotlibwidget.canvas.draw()
        elif self.canvas == 1:
            self.matplotlibwidget_1.canvas.draw()

    # Reset all the parameters
    def reset(self):
        self.G = None
        self.G_original = None
        self.trashbin = None
        self.ResultNetwork = None
        self.CustomNetwork = None
        self.YourScore = 0
        self.ResultScore = 0
        self.poly = None
        self.Start.setEnabled(False)
        self.Confirm.setEnabled(False)
        self.bombwidth, self.bomblength = 2, 2
        self.YourNetwork.setEnabled(False)
        self.ShowAnswer.setEnabled(False)
        self.Original.setEnabled(False)
        self.Clear_ALL()
        self.matplotlibwidget.axis.patches = []
        self.matplotlibwidget_1.axis.patches = []
        self.Start.setEnabled(True)
        self.score_list = list()

        for i in self.cache:
            i.remove()
        self.cache = []
        self.matplotlibwidget_log.canvas.draw()
        self.matplotlibwidget_FINDER.canvas.draw()
        self.bartool_switch(False)
        if self.cidpress is not None:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidpress)
        if self.cidmotion is not None:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidmotion)
        if self.cidrelease is not None:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidrelease)
        if self.colorid is not None:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.colorid)
        if self.hoverconnect is not None:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.hoverconnect)
        if self.clickconnect is not None:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.clickconnect)
        self.cidpress, self.cidmotion, self.cidrelease, self.colorid, self.hoverconnect = None, None, None, None, None
        self.clickconnect = None
    # Choose attack/defend mode
    def modechoose(self):
        self.reset()
        if self.ModeComboBox.currentIndex() == 0:
            self.canvas = 0
            self.ModeParam.setCurrentIndex(1)
        elif self.ModeComboBox.currentIndex() == 1:
            self.canvas = 1
            self.ModeParam.setCurrentIndex(2)

    # Back to the start menu
    def back(self):
        self.ModeParam.setCurrentIndex(0)



    # highlight the hovered node
    def hover(self, event):
        if self.canvas == 0:
            pts = self.b.get_offsets()
        elif self.canvas == 1:
            pts = self.b_1.get_offsets()
        pts_num = len(pts)
        tmp_lines = set()
        new_size_pts = np.ones(pts_num) * 50
        if self.canvas == 0:
            cur_matplotwidget = self.matplotlibwidget
            curr_b = self.b
        elif self.canvas == 1:
            cur_matplotwidget = self.matplotlibwidget_1
            curr_b = self.b_1

        cont, ind = curr_b.contains(event)
        if cont:
            if self.canvas == 0:
                id = self.b.contains(event)[1]['ind'][0]

                edges_plotted = [[tuple(x.get_data()[0]), tuple(x.get_data()[1])] \
                                 for x in self.matplotlibwidget.axis.lines]

            elif self.canvas == 1:
                id = self.b_1.contains(event)[1]['ind'][0]
                edges_plotted = [[tuple(x.get_data()[0]), tuple(x.get_data()[1])] \
                                 for x in self.matplotlibwidget_1.axis.lines]
            tmp_pts = set()
            tmp_pts.add(id)
            edges_plotted = [[(x1, y1), (x2, y2)] for [(x1, x2), (y1, y2)] in edges_plotted]
            pos_dict = nx.get_node_attributes(self.G, 'pos')
            for i in self.G.edges:
                if id in i:
                    # print(pos_dict[i[0]])
                    # print(pos_dict[i[1]])
                    # print(edges_plotted)
                    # return
                    tmp_pts.add(i[0])
                    tmp_pts.add(i[1])
                    tmp_lines_directed_helper = []
                    for j in range(len(edges_plotted)):
                        if pos_dict[i[0]] in edges_plotted[j] and pos_dict[i[1]] in edges_plotted[j]:
                            #print(pos_dict[i[0]])
                            tmp_lines.add(j)
                            cur_matplotwidget.axis.lines[j].set_linewidth(3)
                    if self.directed:
                        find = True
                        while find:
                            find = False
                            for i in cur_matplotwidget.axis.get_children():
                                if isinstance(i, mpl.patches.FancyArrow):
                                    i.remove()
                                    find = True
                        for edge in self.G.edges:
                            if id in edge:
                                tmp_lines_directed_helper.append([pos_dict[edge[0]], pos_dict[edge[1]]])
                        self.switch_directed = True
                        self.draw_arrow(self.G.edges, nx.DiGraph(), tmp_lines_directed_helper)
            for i in tmp_pts:
                new_size_pts[i] = 150
            curr_b.set_sizes(new_size_pts)
            self.draw()
        else:
            for i in cur_matplotwidget.axis.lines:
                i.set_linewidth(1.5)
            curr_b.set_sizes(new_size_pts)
            cur_matplotwidget.canvas.draw()
            if self.directed:
                try:
                    if self.switch_directed:
                        self.switch_directed = False
                        find = True
                        while find:
                            find = False
                            for i in cur_matplotwidget.axis.get_children():
                                if isinstance(i, mpl.patches.FancyArrow):
                                    i.remove()
                                    find = True
                        xydata_b = curr_b.get_offsets()
                        for edge in self.G.edges:
                            cur_matplotwidget.axis.arrow(xydata_b[edge[0]][0], xydata_b[edge[0]][1],
                                                             xydata_b[edge[1]][0] - xydata_b[edge[0]][0],
                                                             xydata_b[edge[1]][1] - xydata_b[edge[0]][1],
                                                             width=0.02, head_width=0.12, length_includes_head=True,
                                                             zorder=2, fc='grey', ec='grey')
                except Exception:
                    pass

    def update_annot(self, ind, text=str):
        pos = self.b.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover_annot(self, event):
        vis = self.annot.get_visible()
        pos = nx.get_node_attributes(self.G, 'pos')
        xydata_b = self.b.get_offsets()
        if event.inaxes == self.matplotlibwidget.axis:
            cont, ind = self.b.contains(event)
            if cont:
                id = self.b.contains(event)[1]['ind'][0]
                for i, j in pos.items():
                    if round(j[0],8) == round(xydata_b[id][0],8) and round(j[1],8) == round(xydata_b[id][1],8):
                        _id = i
                        break
                try:
                    self.update_annot(ind, nx.get_node_attributes(self.G, 'annot')[id][0])
                except Exception:
                    self.update_annot(ind, nx.get_node_attributes(self.G_original, 'annot')[id][0])

                self.annot.set_visible(True)
                self.draw()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.draw()


    # Disconnection
    def default(self):
        if self.moved:
            self.movable_disconnect()
        if self.colored:
            self.changenodecolor_disconnect()

    # Move the node with its edges(drag usage)
    def movable(self):
        self.default()
        self.moved = True
        if self.canvas == 0:
            self.cidpress = self.matplotlibwidget.figure.canvas.mpl_connect(
                'button_press_event', self.on_press_1)
            self.cidrelease = self.matplotlibwidget.figure.canvas.mpl_connect(
                'button_release_event', self.on_release_1)
            self.cidmotion = self.matplotlibwidget.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1)
        elif self.canvas == 1:
            self.cidpress = self.matplotlibwidget_1.figure.canvas.mpl_connect(
                'button_press_event', self.on_press_1)
            self.cidrelease = self.matplotlibwidget_1.figure.canvas.mpl_connect(
                'button_release_event', self.on_release_1)
            self.cidmotion = self.matplotlibwidget_1.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1)
        self.draw()

    def bartool_switch(self,mode):
        if self.canvas == 0:
            self.Drag.setEnabled(mode)
            self.Color.setEnabled(mode)
            self.Spring_Layout.setEnabled(mode)
        elif self.canvas == 1:
            self.Drag_2.setEnabled(mode)
            self.Color_2.setEnabled(mode)
        if not mode:
            self.default()

    # Disconnect the move ids
    def movable_disconnect(self):
        self.moved = False
        if self.canvas == 0:
            self.Drag.setChecked(False)
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidpress)
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidrelease)
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidmotion)
        elif self.canvas == 1:
            self.Drag_2.setChecked(False)
            self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.cidpress)
            self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.cidrelease)
            self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.cidmotion)
        self.draw()

    # Helper function (press) for movable
    def on_press_1(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if not event.inaxes in self.matplotlibwidget.figure.axes and\
                (not event.inaxes in self.matplotlibwidget_1.figure.axes):
            return
        if MainWidget.lock is not None:
            return
        if self.canvas == 0:
            if self.b.contains(event)[0]:
                self.changednode = self.b.contains(event)[1]['ind'][0]
                MainWidget.lock = self
        elif self.canvas == 1:
            if self.b_1.contains(event)[0]:
                self.changednode = self.b_1.contains(event)[1]['ind'][0]
                MainWidget.lock = self

    # Helper function (on move) for movable
    def on_motion_1(self, event):
        'on motion we will move the rect if the mouse is over us'
        if MainWidget.lock is not self:
            return
        if not event.inaxes in self.matplotlibwidget.figure.axes and \
                (not event.inaxes in self.matplotlibwidget_1.figure.axes):
            return
        if self.canvas == 0:
            tmp = self.b.get_offsets()
        elif self.canvas == 1:
            tmp = self.b_1.get_offsets()
        x0, y0 = event.xdata, event.ydata
        tmp[self.changednode] = np.array([x0, y0])
        changed = nx.get_node_attributes(self.G, 'pos')

        changed[self.changednode] = (float(x0), float(y0))
        nx.set_node_attributes(self.G, changed, 'pos')
        self.widget.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor)) # Change the cursor shape
        self.Clear_Lines()
        self.draw_OriginalNetwork()
    # Helper function (release) for movable
    def on_release_1(self, event):
        'on release we reset the press data'
        if MainWidget.lock is not self:
            return
        if self.canvas == 0:
            self.widget.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor)) # Change the cursor shape
        elif self.canvas == 1:
            self.widget_2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))  # Change the cursor shape
        self.press = None
        MainWidget.lock = None


    # Choose which network template to draw
    def choose_and_draw(self):
        self.reset()
        self.bartool_switch(True)
        self.canvas = 0
        index = self.NetworkcomboBox1.currentIndex()
        if self.Directed.isChecked():
            self.directed = True
        else:
            self.directed = False
        if index == 0:
            self.draw_ER_Network()
        elif index == 1:
            self.draw_SW_Network()
        elif index == 2:
            self.draw_BA_Network()
        elif index == 3:
            self.draw_RG_Network()
        self.hoverconnect = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover)  # Connect to hover highlight
        self.hoverconnect_annot = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover_annot)  # Connect to hover annotate


    def draw_BA_Network(self):
        self.attack_method = int(self.Attack_method.currentIndex())
        self.directed = self.Directed.isChecked()

        BA = nx.random_graphs.barabasi_albert_graph(self.NumOfNodes_BA.value(), self.NumOfNewEdge.value())
        self.Make_Random_Point(self.NumOfNodes_BA.value())
        xydata_b = self.b.get_offsets()
        if not self.directed:
            for i in BA.edges():
                self.matplotlibwidget.axis.plot(np.array([xydata_b[i[0]][0], xydata_b[i[1]][0]]),
                                                np.array([xydata_b[i[0]][1], xydata_b[i[1]][1]]),
                                                color="grey", zorder=1)
            self.G = BA
        else:
            G_directed = nx.DiGraph()
            G_directed.add_nodes_from(BA)
            self.draw_arrow(BA.edges, G_directed)
            self.G = G_directed
        pos, annot = dict(), dict()
        for i in range(len(BA.nodes)):
            pos[i] = (xydata_b[i][0], xydata_b[i][1])
            annot[i] = [i]
        nx.set_node_attributes(BA, pos, 'pos')
        nx.set_node_attributes(BA, annot, 'annot')
        self.draw()

    def draw_RG_Network(self):
        self.directed = self.Directed.isChecked()
        self.attack_method = int(self.Attack_method.currentIndex())
        RG = nx.random_geometric_graph(self.NumOfNodes_RG.value(), self.Radius.value())
        self.Make_Random_Point(self.NumOfNodes_RG.value())
        xydata_b = self.b.get_offsets()
        if not self.directed:
            for i in RG.edges():
                self.matplotlibwidget.axis.plot(np.array([xydata_b[i[0]][0], xydata_b[i[1]][0]]),
                                                np.array([xydata_b[i[0]][1], xydata_b[i[1]][1]]),
                                                color="grey", zorder=1)
            self.G = RG
        else:
            G_directed = nx.DiGraph()
            G_directed.add_nodes_from(RG)
            pos = dict()
            for i in range(len(G_directed.nodes)):
                pos[i] = (xydata_b[i][0], xydata_b[i][1])
            nx.set_node_attributes(G_directed, pos, 'pos')
            self.draw_arrow(RG.edges, G_directed)
            self.G = G_directed
        pos, annot = dict(), dict()
        for i in range(len(RG.nodes)):
            pos[i] = (xydata_b[i][0], xydata_b[i][1])
            annot[i] = [i]
        nx.set_node_attributes(RG, pos, 'pos')
        nx.set_node_attributes(RG, annot, 'annot')
        self.draw()

    def draw_SW_Network(self):
        self.directed = self.Directed.isChecked()
        self.attack_method = int(self.Attack_method.currentIndex())
        self.Make_Random_Point(self.NumOfNodes_SW.value())
        SW = nx.random_graphs.watts_strogatz_graph(self.NumOfNodes_SW.value(),
                                                   self.NumOfNeigh.value(),
                                                   self.SW_prob.value())
        xydata_b = self.b.get_offsets()
        if not self.directed:
            for i in SW.edges():
                self.matplotlibwidget.axis.plot(np.array([xydata_b[i[0]][0], xydata_b[i[1]][0]]),
                                                np.array([xydata_b[i[0]][1], xydata_b[i[1]][1]]),
                                                color="grey", zorder=1)
            self.G = SW
        else:
            G_directed = nx.DiGraph()
            G_directed.add_nodes_from(SW)
            self.draw_arrow(SW.edges, G_directed)
            self.G = G_directed
        pos, annot = dict(), dict()
        for i in range(len(self.G.nodes)):
            pos[i] = (xydata_b[i][0], xydata_b[i][1])
            annot[i] = [i]
        nx.set_node_attributes(self.G, pos, 'pos')
        nx.set_node_attributes(self.G, annot, 'annot')
        self.draw()

    def draw_ER_Network(self):
        self.attack_method = int(self.Attack_method.currentIndex())
        self.Make_Random_Point(self.NumOfNodes_ER.value())
        ER = nx.random_graphs.erdos_renyi_graph(self.NumOfNodes_ER.value(), self.ER_prob.value())
        xydata_b = self.b.get_offsets()
        if not self.directed:
            for i in ER.edges():
                self.matplotlibwidget.axis.plot(np.array([xydata_b[i[0]][0], xydata_b[i[1]][0]]),
                                                np.array([xydata_b[i[0]][1], xydata_b[i[1]][1]]),
                                                color="grey", zorder=1)
            self.G = ER
        else:
            G_directed = nx.DiGraph()
            G_directed.add_nodes_from(ER)
            self.draw_arrow(ER.edges, G_directed)
            self.G = G_directed
        pos, annot = dict(), dict()
        for i in range(len(self.G.nodes)):
            pos[i] = (xydata_b[i][0], xydata_b[i][1])
            annot[i] = [i]
        nx.set_node_attributes(self.G, pos, 'pos')
        nx.set_node_attributes(self.G, annot, 'annot')
        self.draw()

    # Attack by edge main function
    def attack_by_edge(self, num_of_edges):
        self.limit = num_of_edges
        self.count = 0
        self.G_original = self.G.copy()
        self.hoverconnect = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover)
        self.clickconnect = self.matplotlibwidget.figure.canvas.mpl_connect(
            'button_press_event', self.attack_by_edge_mouseclick)

    # Attack by edge helper function (attack and draw)
    def attack_by_edge_mouseclick(self, event):
        xdata, ydata = event.xdata, event.ydata
        result = self.attack_by_edge_helper(xdata, ydata)
        edges = list(self.G.edges())
        if result[0]:
            self.count += 1
            chosen_edge = result[1:]
            for edge_i in range(len(edges)):
                if chosen_edge == edges[edge_i]:
                    self.G.remove_edge(result[1],result[2])
        self.Clear_Lines()
        self.draw_answer_network(self.G, nx.Graph(), 0, 0, 0, 0, self.b.get_offsets(), False, "custom")
        if self.count == self.limit:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.clickconnect)
        self.draw()

    # Attack by edge helper function(test if mouse click is on the edge)
    def attack_by_edge_helper(self, xdata, ydata):
        pos = nx.get_node_attributes(self.G, 'pos')
        edges = self.G.edges()
        for n, m in edges:
            n_pos, m_pos = pos[n], pos[m]
            x1, y1 = n_pos[0], n_pos[1]
            x2, y2 = m_pos[0], m_pos[1]
            # Ax + By + C = 0
            A = y2 - y1
            B = x1 - x2
            C = x2 * y1 - x1* y2
            D = A * xdata + B * ydata + C
            if -0.5 <= D <= 0.5:
                return True, n, m
        return False, None, None
    # attack by point main method
    def attack_by_point(self, num_of_points):
        self.ShowAnswer.setEnabled(True)
        self.FINDER_result.clear()
        self.G_original = self.copy_graph()
        nx.write_gml(self.G, '../data/synthetic/uniform_cost/00/g_0')
        self.limit = num_of_points
        self.trashbin = []
        self.count = 0
        self.hoverconnect = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover)
        self.clickconnect = self.matplotlibwidget.figure.canvas.mpl_connect(
            'button_press_event', self.attack_by_point_mouseclick)

    def copy_graph(self):
        if self.directed:
            return nx.freeze(nx.to_directed(self.G))
        else:
            if self.attack_method == 1 and self.G_original is not None:
                ret = nx.create_empty_copy(self.G_original)
                ret.add_edges_from(self.G_original.edges())
                nx.set_node_attributes(ret, nx.get_node_attributes(self.G_original, 'pos'), 'pos')
            else:
                ret = nx.create_empty_copy(self.G)
                ret.add_edges_from(self.G.edges())
                nx.set_node_attributes(ret, nx.get_node_attributes(self.G, 'pos'),'pos')
            return ret
    # Attack by point helper function
    def attack_by_point_mouseclick(self, event):
        pts = self.b.get_offsets()
        if self.b.contains(event)[0]:
            id = self.b.contains(event)[1]['ind'][0]
            self.trashbin.append(self.b.get_offsets()[id])
            pts_new = np.delete(pts, id, axis=0)
            self.b.set_offsets(pts_new)
            self.draw()
            self.G.remove_node(id)
            new_nodes = [x for x in range(len(pts_new))]
            mapping = dict()
            nodes = list(self.G.nodes())

            for i in range(len(new_nodes)):
                mapping[nodes[i]] = new_nodes[i]
            self.G = nx.relabel_nodes(self.G, mapping)
            self.Clear_Lines()
            self.draw_answer_network(self.G, nx.Graph(), 0, 0, 0, 0, pts, False, "custom")
            self.count += 1
        if self.count == self.limit:
            self.matplotlibwidget.figure.canvas.mpl_disconnect(self.clickconnect)

    def attack_by_bomb_continuous(self):
        self.bombwidth, self.bomblength = int(self.bombwidth_input_2.value()), int(self.bomblength_input_2.value())
        self.img = Image.open('C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/bomb.jpg')
        self.img.putalpha(128)
        newsize = (49 * self.bombwidth, 49 * self.bomblength)
        self.img = self.img.resize(newsize)
        self.imagebox = OffsetImage(self.img, zoom=1)
        self.imagebox.set(alpha=0.1, visible=False, zorder=2)

        self.ab = AnnotationBbox(self.imagebox, (1, 1), frameon=False)
        self.newab = None
        self.matplotlibwidget.axis.add_artist(self.ab)

        self.cidpress = self.matplotlibwidget.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.matplotlibwidget.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.draw()

    def attack_by_bomb(self):
        self.bombwidth, self.bomblength = int(self.bombwidth_input.value()), int(self.bomblength_input.value())
        self.img = Image.open('C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/bomb.jpg')
        self.img.putalpha(128)
        newsize = (49 * self.bombwidth, 49 * self.bomblength)
        self.img = self.img.resize(newsize)
        self.imagebox = OffsetImage(self.img, zoom=1)
        self.imagebox.set(alpha=0.1, visible=False, zorder=2)

        self.ab = AnnotationBbox(self.imagebox, (1, 1), frameon=False)
        self.newab = None
        self.matplotlibwidget.axis.add_artist(self.ab)

        self.cidpress = self.matplotlibwidget.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.matplotlibwidget.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.matplotlibwidget.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)
        self.draw()

    # Draw the arrow (if hover highlight is needed)
    def draw_arrow(self, edges, G_directed, helper_list=None):
        if self.canvas == 0:
            xydata_b = self.b.get_offsets()
            cur_matplotlibwidget = self.matplotlibwidget
        elif self.canvas == 1:
            xydata_b = self.b_1.get_offsets()
            cur_matplotlibwidget = self.matplotlibwidget_1
        if helper_list:
            for edge in self.G.edges:
                for hover_edge in helper_list:
                    if xydata_b[edge[0]][0] == hover_edge[0][0] \
                            and xydata_b[edge[0]][1] == hover_edge[0][1] \
                            and xydata_b[edge[1]][1] == hover_edge[1][1] \
                            and xydata_b[edge[1]][0] == hover_edge[1][0]:
                        cur_matplotlibwidget.axis.arrow(xydata_b[edge[0]][0], xydata_b[edge[0]][1],
                                                         xydata_b[edge[1]][0] - xydata_b[edge[0]][0],
                                                         xydata_b[edge[1]][1] - xydata_b[edge[0]][1],
                                                         width=0.04, head_width=0.24, length_includes_head=True,
                                                         zorder=2, fc='grey', ec='grey')

                    else:
                        cur_matplotlibwidget.axis.arrow(xydata_b[edge[0]][0], xydata_b[edge[0]][1],
                                                         xydata_b[edge[1]][0] - xydata_b[edge[0]][0],
                                                         xydata_b[edge[1]][1] - xydata_b[edge[0]][1],
                                                         width=0.02, head_width=0.12, length_includes_head=True,
                                                         zorder=2, fc='grey', ec='grey')
        else:
            for i in edges:
                tmp_1 = np.random.choice([0, 1], p=[0.5, 0.5])
                if tmp_1:
                    edge = i
                    G_directed.add_edge(edge[0], edge[1])
                    cur_matplotlibwidget.axis.arrow(xydata_b[edge[0]][0], xydata_b[edge[0]][1],
                                                     xydata_b[edge[1]][0] - xydata_b[edge[0]][0],
                                                     xydata_b[edge[1]][1] - xydata_b[edge[0]][1],
                                                     width=0.02, head_width=0.12, length_includes_head=True,
                                                     zorder=2, fc='grey', ec='grey')
                tmp_2 = np.random.choice([0, 1], p=[0.5, 0.5])
                if tmp_2:
                    edge = (i[1], i[0])
                    G_directed.add_edge(edge[0], edge[1])
                    cur_matplotlibwidget.axis.arrow(xydata_b[edge[0]][0], xydata_b[edge[0]][1],
                                                     xydata_b[edge[1]][0] - xydata_b[edge[0]][0],
                                                     xydata_b[edge[1]][1] - xydata_b[edge[0]][1],
                                                     width=0.02, head_width=0.12, length_includes_head=True,
                                                     zorder=2, fc='grey', ec='grey')


    # # Draw custom network with bomb attack affected
    # def make_custom_graph(self):
    #     if self.directed:
    #         Graph = nx.DiGraph()
    #     else:
    #         Graph = nx.Graph()
    #     content = self.adjacency_list.toPlainText()
    #     self.edge = []
    #     # for i in content[1:-1]:
    #     #     if i == '[':
    #     #         tmp = []
    #     #     elif i == ']':
    #     #         self.edge.append(tmp)
    #     #     elif i.isdigit():
    #     #         tmp.append(int(i))
    #     # Graph.add_nodes_from(i for i in range(len(self.edge)))
    #     edge1 = []
    #
    #     for i in range(len(self.edge)):
    #         for j in self.edge[i]:
    #             edge1.append((i, j))
    #     Graph.add_edges_from(edge1)
    #     self.G = Graph


    # Draw random points (helper function for drawing)
    def Make_Random_Point(self, n, pos = None):
        if pos:
            for (i, j) in pos:
                if self.canvas == 1:
                    xydata_b = self.b_1.get_offsets()
                elif self.canvas == 0:
                    xydata_b = self.b.get_offsets()
                new_xydata_b = np.row_stack((xydata_b, np.array([i, j])))
                if self.canvas == 1:
                    self.b_1.set_offsets(new_xydata_b)
                elif self.canvas == 0:
                    self.b.set_offsets(new_xydata_b)
        else:
            for k in range(n):
                if self.canvas == 1:
                    xydata_b = self.b_1.get_offsets()
                elif self.canvas == 0:
                    xydata_b = self.b.get_offsets()
                while n:
                    x = np.random.uniform(0, 10)
                    y = np.random.uniform(0, 10)
                    found = False
                    for i in xydata_b:
                        if [x, y] == list(i):
                            found = True
                            break
                    if not found:
                        break
                new_xydata_b = np.row_stack((xydata_b, np.array([x, y])))

                if self.canvas == 1:
                    self.b_1.set_offsets(new_xydata_b)
                elif self.canvas == 0:
                    self.b.set_offsets(new_xydata_b)
        self.draw()

    # Clear all the nodes and edges
    def Clear_ALL(self):

        self.b.set_offsets(np.ndarray((0, 2)))
        self.b.set_facecolors("red")
        self.b.set_edgecolors("red")
        if self.canvas == 0:
            while self.matplotlibwidget.axis.lines:
                self.matplotlibwidget.axis.lines.remove(self.matplotlibwidget.axis.lines[0])
            tmp = self.matplotlibwidget.axis.get_children()
            idx = 0
            for i in range(len(tmp)):
                if isinstance(tmp[i], mpl.patches.FancyArrow):
                    idx = i
                    break
            while isinstance((self.matplotlibwidget.axis.get_children()[idx]), mpl.patches.FancyArrow):
                self.matplotlibwidget.axis.get_children()[idx].remove()
            # while isinstance((self.matplotlibwidget.axis.get_children()[2]), mpl.patches.FancyArrow):
            #     self.matplotlibwidget.axis.get_children()[2].remove()
            try:
                matplotlib.artist.Artist.remove(self.ab)
            except Exception:
                pass
        elif self.canvas == 1:
            self.b_1.set_offsets(np.ndarray((0, 2)))
            while self.matplotlibwidget_1.axis.lines:
                self.matplotlibwidget_1.axis.lines.remove(self.matplotlibwidget_1.axis.lines[0])
            while isinstance((self.matplotlibwidget_1.axis.get_children()[1]), mpl.patches.FancyArrow):
                self.matplotlibwidget_1.axis.get_children()[1].remove()
            try:
                matplotlib.artist.Artist.remove(self.ab)
            except Exception:
                pass
        self.draw()

    # Find GCC (not directed) or SCC (directed)
    def GCC_or_SCC(self, draw=True):
        if self.ResultNetwork is not None:
            self.Clear_ALL()
            if self.attack_method == 1:
                draw_bomb = False
            elif self.attack_method == 0:
                draw_bomb = True
            Graph = self.ResultNetwork[0]
            pos = nx.get_node_attributes(Graph, 'pos')
            self.Make_Random_Point(0, pos.values())
            self.draw_answer_network(self.ResultNetwork[0],
                                     self.ResultNetwork[1],
                                     self.ResultNetwork[2],
                                     self.ResultNetwork[3],
                                     self.ResultNetwork[4],
                                     self.ResultNetwork[5],
                                     self.ResultNetwork[6],
                                     draw_bomb, None)
            if self.attack_method == 1:
                BestGCC = "Best GCC: " + str(len(self.ResultNetwork[1])) + '\n'
                mesBox = QMessageBox()
                mesBox.setText("Score")
                mesBox.setInformativeText(BestGCC)
                mesBox.exec_()
            return
        if self.attack_method == 1:
            testSynthetic.FINDER_get()
            # f = open('../results/FINDER_ND/synthetic/result.txt')
            ans_str = []
            ans_int = []
            with open('../results/FINDER_ND/synthetic/result.txt') as f:
                l = f.readline()
                tmp = ''
                for i in range(len(l)):
                    # if l[i].isdigit():
                    #     if l[i+1].isdigit():
                    #         ans_str.append(l[i] + l[i+1])
                    #         ans_int.append(int(l[i] + l[i+1]))
                    #         i = i+ 1
                    #         continue
                    #     ans_str.append(l[i])
                    #     ans_int.append(int(l[i]))
                    #     if len(ans_str) == int(self.point_num.value()):
                    #         break
                    if len(ans_str) == int(self.point_num.value()):
                        break
                    if l[i].isdigit():
                        tmp += l[i]
                    else:
                        if tmp != '':
                            ans_str.append(tmp)
                            ans_int.append(int(tmp))
                            tmp = ''
            self.FINDER_result.append(' -> '.join(ans_str))
            ans_G = self.copy_graph()
            ans_G = nx.Graph(ans_G)
            pos = nx.get_node_attributes(self.G_original,'pos')
            ans_G.remove_nodes_from(ans_int)
            xydata_b = self.b.get_offsets()
            # print('ans_G attributes', ans_G.nodes(), ans_G.edges())
            if not self.directed:
                G0 = self.Find_GCC(ans_G)
            else:
                G0 = self.Find_SCC(ans_G)
            self.Clear_ALL()
            new_pos = []
            for i in pos:
                if i in ans_G.nodes():
                    new_pos.append(pos[i])
            self.Make_Random_Point(0, new_pos)
            # self.G = ans_G
            self.draw_answer_network(ans_G, G0, 0, 0, 0, 0, xydata_b, False, "result")
            BestGCC = "Best GCC: " + str(len(G0)) + '\n'
            mesBox = QMessageBox()
            mesBox.setText("Score")
            mesBox.setInformativeText( BestGCC)
            mesBox.exec_()
            self.ResultNetwork = [ans_G, G0.copy(), 0,0,0,0, xydata_b]

            for i in range(len(ans_int)):
                ans_G = self.copy_graph()
                ans_G = nx.Graph(ans_G)
                ans_G.remove_nodes_from(ans_int[:i+1])
                if not self.directed:
                    G0 = self.Find_GCC(ans_G)
                else:
                    G0 = self.Find_SCC(ans_G)
                score = len(G0)
                self.score_list.append(score)
            tmp = self.matplotlibwidget_FINDER.axis.bar(range(len(self.score_list)),
                                                     self.score_list,
                                                     width=0.5,
                                                     color=(0, 0.584, 0.714))
            self.autolabel(tmp)
            self.cache.append(tmp)
            if len(self.score_list) > 0:
                self.matplotlibwidget_FINDER.axis.set_xticks(range(0, len(self.score_list), 1))
                self.matplotlibwidget_FINDER.axis.set_yticks(range(0, max(self.score_list),
                                                                max(1, int(max(self.score_list) / 5))))
            self.matplotlibwidget_FINDER.canvas.draw()
            return
        self.Clear_Lines()
        xydata_b = self.b.get_offsets()


        degree_dict = dict()
        # pos = dict()
        # for i in range(len(self.G.nodes)):
        #     pos[i] = (xydata_b[i][0], xydata_b[i][1])
        # nx.set_node_attributes(self.G, pos, 'pos')
        Graph = self.G.copy()

        for (i, j) in Graph.degree:
            degree_dict[i] = j
        degree_sort = sorted(Graph.degree, key=lambda i: i[1], reverse=True)

        bomblength, bombwidth = self.bomblength, self.bombwidth

        _xlb, _ylb = 0, 0
        degree_curr = 0
        Graph = self.remove_redundant_points(Graph, self.b) # make a copy of graph with redundant nodes (0 degreee)
        # removed
        pos = nx.get_node_attributes(Graph, 'pos')

        index = int(len(degree_sort) / 5) # Choose approximately 20% nodes to do greedy algo

        for i in degree_sort[:max(index, 1)]:
            point = i[0]
            try:
                for xlb in range(max(int(pos[point][0]) - bombwidth, 0),
                                 min(int(pos[point][0]) + 1, 10 - bombwidth + 1)):
                    for ylb in range(max(int(pos[point][1]) - bomblength, 0),
                                     min(int(pos[point][1]) + 1, 10 - bomblength + 1)):
                        tmpdegree = 0
                        for i in pos:
                            if xlb + bombwidth >= pos[i][0] >= xlb \
                                    and ylb + bomblength >= pos[i][1] >= ylb:
                                tmpdegree += degree_dict[i]
                        if tmpdegree > degree_curr:
                            degree_curr = tmpdegree
                            _xlb = xlb
                            _ylb = ylb
            except Exception:
                print("pos", pos, "point", point)

        new_edges = find_undirected(Graph, _xlb, _ylb, bombwidth, bomblength) # Find edges remained
        G = nx.create_empty_copy(Graph)
        G.add_edges_from(new_edges)

        if self.directed:
            G0 = self.Find_SCC(G)
        else:
            G0 = self.Find_GCC(G)

        self.ResultNetwork = [G.copy(), G0.copy(), _xlb, _ylb, bombwidth, bomblength, xydata_b]
        if draw:
            self.draw_answer_network(G, G0, _xlb, _ylb, bombwidth, bomblength, xydata_b, True, "result")
        return G0

    # Draw the answer network
    def draw_answer_network(self, G, G0, _xlb, _ylb, bombwidth, bomblength, xydata_b, draw_bomb, attribute):
        pos = nx.get_node_attributes(G, 'pos')
        if not self.directed:
            for i in G.edges():
                if self.canvas == 0:
                    self.matplotlibwidget.axis.plot(np.array([pos[i[0]][0], pos[i[1]][0]]),
                                                    np.array([pos[i[0]][1], pos[i[1]][1]]),
                                                    color="grey", zorder=1)
                elif self.canvas == 1:
                    self.matplotlibwidget_1.axis.plot(np.array([pos[i[0]][0], pos[i[1]][0]]),
                                                      np.array([pos[i[0]][1], pos[i[1]][1]]),
                                                      color="grey", zorder=1)

            for i in G0.edges():
                if self.canvas == 0:
                    self.matplotlibwidget.axis.plot(np.array([pos[i[0]][0], pos[i[1]][0]]),
                                                    np.array([pos[i[0]][1], pos[i[1]][1]]),
                                                    color="pink", zorder=2)
                elif self.canvas == 1:
                    self.matplotlibwidget_1.axis.plot(np.array([pos[i[0]][0], pos[i[1]][0]]),
                                                      np.array([pos[i[0]][1], pos[i[1]][1]]),
                                                      color="pink", zorder=2)
        else:
            for i in G.edges():
                if i in G0.edges:
                    if self.canvas == 0:
                        self.matplotlibwidget.axis.arrow(pos[i[0]][0], pos[i[0]][1],
                                                         pos[i[1]][0] - pos[i[0]][0],
                                                         pos[i[1]][1] - pos[i[0]][1],
                                                         width=0.02, head_width=0.12, length_includes_head=True,
                                                         zorder=3, fc='pink', ec='pink')
                    elif self.canvas == 1:
                        self.matplotlibwidget_1.axis.arrow(pos[i[0]][0], pos[i[0]][1],
                                                         pos[i[1]][0] - pos[i[0]][0],
                                                         pos[i[1]][1] - pos[i[0]][1],
                                                         width=0.02, head_width=0.12, length_includes_head=True,
                                                         zorder=3, fc='pink', ec='pink')
                else:
                    if self.canvas == 0:
                        self.matplotlibwidget.axis.arrow(pos[i[0]][0], pos[i[0]][1],
                                                     pos[i[1]][0] - pos[i[0]][0],
                                                     pos[i[1]][1] - pos[i[0]][1],
                                                     width=0.02, head_width=0.12, length_includes_head=True,
                                                     zorder=2, fc='grey', ec='grey')
                    if self.canvas == 1:
                        self.matplotlibwidget_1.axis.arrow(pos[i[0]][0], pos[i[0]][1],
                                                     pos[i[1]][0] - pos[i[0]][0],
                                                     pos[i[1]][1] - pos[i[0]][1],
                                                     width=0.02, head_width=0.12, length_includes_head=True,
                                                     zorder=2, fc='grey', ec='grey')
        if draw_bomb:
            try:
                matplotlib.artist.Artist.remove(self.ab)
            except Exception:
                pass
            finalx = _xlb + float(self.bombwidth / 2)
            finaly = _ylb + float(self.bomblength / 2)
            self.ab = AnnotationBbox(self.imagebox, [finalx, finaly], frameon=False)
            if self.canvas == 0:
                self.matplotlibwidget.axis.add_artist(self.ab)
            elif self.canvas == 1:
                self.matplotlibwidget_1.axis.add_artist(self.ab)
        self.draw()
        self.YourScore = len(G0.edges)
        if attribute == "result":
            self.ResultNetwork = [G.copy(), G0.copy(), _xlb, _ylb, bombwidth, bomblength, xydata_b]
        elif attribute == "custom":
            self.CustomNetwork = [G.copy(), G0.copy(), _xlb, _ylb, bombwidth, bomblength, xydata_b]

    # Clear all the edges
    def Clear_Lines(self):
        if self.canvas == 0:
            while self.matplotlibwidget.axis.lines:
                self.matplotlibwidget.axis.lines.remove(self.matplotlibwidget.axis.lines[0])
            while isinstance((self.matplotlibwidget.axis.get_children()[1]), mpl.patches.FancyArrow):
                self.matplotlibwidget.axis.get_children()[1].remove()
        elif self.canvas == 1:
            while self.matplotlibwidget_1.axis.lines:
                self.matplotlibwidget_1.axis.lines.remove(self.matplotlibwidget_1.axis.lines[0])
            while isinstance((self.matplotlibwidget_1.axis.get_children()[1]), mpl.patches.FancyArrow):
                self.matplotlibwidget_1.axis.get_children()[1].remove()

        try:
            matplotlib.artist.Artist.remove(self.ab)
        except Exception:
            pass

    # Helper function to find GCC
    def Find_GCC(self, G):
        Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
        G0 = G.subgraph(Gcc[0])
        return G0

    # Helper function to find SCC
    def Find_SCC(self, G):
        Scc = sorted(nx.strongly_connected_components(G), key=len, reverse=True)
        G0 = G.subgraph(Scc[0])
        return G0

    # Remove nodes with 0 degree
    def remove_redundant_points(self, G, b):
        tmp = []
        for i in G.degree:
            if i[1] == 0:
                tmp.append(i[0])
        G.remove_nodes_from(tmp)
        return G

    # Draw the original network
    def draw_OriginalNetwork(self):
        self.Clear_ALL()
        pos = nx.get_node_attributes(self.G,'pos').values()
        self.Make_Random_Point(0, pos)
        if not self.G_original:
            graph = self.G
        else:
            graph = self.G_original
        pos = nx.get_node_attributes(graph, 'pos')

        if self.trashbin is not None:
            for i in self.trashbin:
                new_xydata_b = np.insert(self.b.get_offsets(), 0, i, axis=0)
                self.b.set_offsets(new_xydata_b)
                self.draw()

        if not self.directed:
            for i in graph.edges():
                if self.canvas == 0:
                    self.matplotlibwidget.axis.plot(np.array([pos[i[0]][0], pos[i[1]][0]]),
                                                    np.array([pos[i[0]][1], pos[i[1]][1]]),
                                                    color="grey", zorder=1)
                if self.canvas == 1:
                    self.matplotlibwidget_1.axis.plot(np.array([pos[i[0]][0], pos[i[1]][0]]),
                                                      np.array([pos[i[0]][1], pos[i[1]][1]]),
                                                      color="grey", zorder=1)
        else:
            for edge in graph.edges():
                if self.canvas == 0:
                    self.matplotlibwidget.axis.arrow(pos[edge[0]][0], pos[edge[0]][1],
                                                     pos[edge[1]][0] - pos[edge[0]][0],
                                                     pos[edge[1]][1] - pos[edge[0]][1],
                                                     width=0.02, head_width=0.12, length_includes_head=True,
                                                     zorder=2, fc='grey', ec='grey')
                if self.canvas == 1:
                    self.matplotlibwidget_1.axis.arrow(pos[edge[0]][0], pos[edge[0]][1],
                                                       pos[edge[1]][0] - pos[edge[0]][0],
                                                       pos[edge[1]][1] - pos[edge[0]][1],
                                                       width=0.02, head_width=0.12, length_includes_head=True,
                                                       zorder=2, fc='grey', ec='grey')
        self.draw()
    # Draw the bomb
    def start_attack(self):
        self.matplotlibwidget.figure.canvas.mpl_disconnect(self.hoverconnect)
        self.bartool_switch(False)
        try:
            self._disconnect()
        except:
            pass
        self.Start.setEnabled(False)
        self.Confirm.setEnabled(True)
        self.press = None
        if self.attack_method == 0:
            self.attack_by_bomb()
        elif self.attack_method == 1:
            self.attack_by_point(int(self.point_num.value()))
        elif self.attack_method == 2:
            self.attack_by_edge(int(self.edge_num.value()))
        elif self.attack_method == 3:
            self.attack_by_bomb_continuous()

    def autolabel(self, rects):
        for rect in rects:
            height = rect.get_height()
            if self.attack_method == 3:
                tmp = self.matplotlibwidget_log.axis.text(rect.get_x() + rect.get_width() / 2. - 0.08,
                                                      1.03 * height,
                                                      '%s' % int(height), size=10)
            elif self.attack_method == 1:
                tmp = self.matplotlibwidget_FINDER.axis.text(rect.get_x() + rect.get_width() / 2. - 0.08,
                                                          1.03 * height,
                                                          '%s' % int(height), size=10)
            self.cache.append(tmp)

    def draw_custom_result(self):
        self.Drag.setEnabled(False)
        self.Color.setEnabled(False)
        self.Spring_Layout.setEnabled(False)
        if self.attack_method == 0:
            self.Original.setEnabled(True)
            self.YourNetwork.setEnabled(True)
            self.ShowAnswer.setEnabled(True)
            self.Confirm.setEnabled(False)
            if self.CustomNetwork is not None:
                self.Clear_Lines()
                self.draw_answer_network(self.CustomNetwork[0],
                                         self.CustomNetwork[1],
                                         self.CustomNetwork[2],
                                         self.CustomNetwork[3],
                                         self.CustomNetwork[4],
                                         self.CustomNetwork[5],
                                         self.CustomNetwork[6],
                                         True, None)
                return
            self.Clear_Lines()
            xydata_b = self.b.get_offsets()

            new_edges = find_undirected(self.G, self.custom_xlb, self.custom_ylb, self.bombwidth, self.bomblength)
            G = nx.create_empty_copy(self.G)
            G.add_edges_from(new_edges)
            if not self.directed:
                G0 = self.Find_GCC(G)
            else:
                G0 = self.Find_SCC(G)
            self.CustomNetwork = [G.copy(), G0.copy(), self.custom_xlb,
                                  self.custom_ylb, self.bombwidth, self.bomblength, xydata_b]
            self.draw_answer_network(G, G0, self.custom_xlb, self.custom_ylb,
                                     self.bombwidth, self.bomblength, xydata_b, False, "custom")
            YourGCC = "Your GCC: " + str(len(G0)) + '\n'
            BestGCC = "Best GCC: " + str(len(self.GCC_or_SCC(False))) + '\n'
            mesBox = QMessageBox()
            answer = mesBox.addButton("Show Answer", QMessageBox.YesRole)
            answer.clicked.connect(self.GCC_or_SCC)
            mesBox.setText("Score")
            mesBox.setInformativeText(YourGCC + BestGCC)
            mesBox.exec_()
            self._disconnect()
        elif self.attack_method == 1 or self.attack_method == 2:
            self.Clear_Lines()
            self.Original.setEnabled(True)
            self.YourNetwork.setEnabled(True)
            self.ShowAnswer.setEnabled(True)
            self.Confirm.setEnabled(False)
            xydata_b = self.b.get_offsets()
            new_edges = find_undirected(self.G, 0, 0, 0, 0)
            G = nx.create_empty_copy(self.G)
            G.add_edges_from(new_edges)
            if not self.directed:
                G0 = self.Find_GCC(G)
            else:
                G0 = self.Find_SCC(G)
            self.CustomNetwork = [G.copy(), G0.copy(), 0, 0, 0, 0, xydata_b]
            self.draw_answer_network(G, G0, 0, 0, 0, 0, xydata_b, False, "custom")
            YourGCC = "Your GCC: " + str(len(G0)) + '\n'
            # BestGCC = "Best GCC: " + str(len(self.GCC_or_SCC(False))) + '\n'
            mesBox = QMessageBox()
            answer = mesBox.addButton("Show Answer", QMessageBox.YesRole)
            answer.clicked.connect(self.GCC_or_SCC)
            mesBox.setText("Score")
            mesBox.setInformativeText(YourGCC)# + BestGCC)
            mesBox.exec_()
        elif self.attack_method == 3:
            self.Confirm.setEnabled(False)
            if self.CustomNetwork is not None:
                self.Clear_Lines()
            self.Clear_Lines()
            xydata_b = self.b.get_offsets()
            new_edges = find_undirected(self.G, self.custom_xlb, self.custom_ylb, self.bombwidth, self.bomblength)
            G = nx.create_empty_copy(self.G)
            G.add_edges_from(new_edges)
            if not self.directed:
                G0 = self.Find_GCC(G)
            else:
                G0 = self.Find_SCC(G)
            self.draw_answer_network(G, G0, self.custom_xlb, self.custom_ylb,
                                     self.bombwidth, self.bomblength, xydata_b, False, "custom")
            self.G = G
            self._disconnect()
            score = len(G0)
            self.score_list.append(score)
            tmp = self.matplotlibwidget_log.axis.bar(range(len(self.score_list)),
                                                     self.score_list,
                                                     width=0.5,
                                                     color = (0, 0.584, 0.714))
            self.autolabel(tmp)
            self.cache.append(tmp)
            if len(self.score_list) > 0:
                self.matplotlibwidget_log.axis.set_xticks(range(0,len(self.score_list),1))
                self.matplotlibwidget_log.axis.set_yticks(range(0,max(self.score_list),
                                                                max(1,int(max(self.score_list)/5))))
            self.matplotlibwidget_log.canvas.draw()
            if score > 2:
                self.attack_method = 3
                self.start_attack()
            else:
                mesBox = QMessageBox()
                mesBox.setIcon(QMessageBox.Information)
                mesBox.setText("Note: The network has collapsed!")
                mesBox.exec_()


    # Draw custom result under defend mode
    def draw_custom_result_2(self):
        self.Confirm_2.setEnabled(False)
        self.Original_2.setEnabled(True)
        self.ShowResult.setEnabled(True)
        self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.cidpress)
        self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.cidrelease)

        self.canvas = 1
        self.Clear_Lines()

        self.img = Image.open('C:/Users/shiti/Desktop/urpn/FINDER/FINDER_ND/pics/bomb.jpg')
        self.img.putalpha(128)
        newsize = (57 * self.bombwidth, 55 * self.bomblength)
        self.img = self.img.resize(newsize)
        self.imagebox = OffsetImage(self.img, zoom=1)
        self.imagebox.set(alpha=0.1, visible=False, zorder=2)
        mesBox = QMessageBox()
        mesBox.setText("Score")
        if not self.directed:
            BestGCC = "Your GCC: " + str(len(self.GCC_or_SCC(True))) + '\n'
            mesBox.setInformativeText(BestGCC)
        else:
            BestSCC = "Your SCC: " + str(len(self.GCC_or_SCC(True))) + '\n'
            mesBox.setInformativeText(BestSCC)
        mesBox.exec_()

    # Show result of defend mode
    def Show_Result(self):
        self.Confirm_2.setEnabled(False)
        self.Clear_Lines()
        self.draw_answer_network(self.ResultNetwork[0],
                                 self.ResultNetwork[1],
                                 self.ResultNetwork[2],
                                 self.ResultNetwork[3],
                                 self.ResultNetwork[4],
                                 self.ResultNetwork[5],
                                 self.ResultNetwork[6],
                                 True, 'result')
        return

    # Helper function for drawing bomb
    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.ab.axes:
            return
        if MainWidget.lock is not None:
            return
        contains, attrd = self.ab.contains(event)
        if not contains:
            return
        if not self.newab:
            x0, y0 = self.ab.xy
        else:
            x0, y0 = self.newab.xy

        self.press = x0, y0, event.xdata, event.ydata
        MainWidget.lock = self

    # Helper function for drawing bomb
    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if MainWidget.lock is not self:
            return
        x, y = self.ab.xy
        if not (0 <= x <= 10) or not (0 <= y <= 10):
            return
        if event.inaxes != self.ab.axes and (not event.inaxes in self.matplotlibwidget.figure.axes):
            return
        self.widget.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        matplotlib.artist.Artist.remove(self.ab)
        self.ab = AnnotationBbox(self.imagebox, [x0 + dx, y0 + dy], frameon=False)
        self.matplotlibwidget.axis.add_artist(self.ab)
        self.draw()

    # Helper function for drawing bomb
    def on_release(self, event):
        'on release we reset the press data'
        if MainWidget.lock is not self:
            return
        self.widget.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.press = None
        MainWidget.lock = None
        x, y = self.ab.xy
        matplotlib.artist.Artist.remove(self.ab)
        if self.bomblength % 2 == 1:
            finaly = round(y) + 0.5
        else:
            finaly = round(y)
        if self.bombwidth % 2 == 1:
            finalx = round(x) + 0.5
        else:
            finalx = round(x)
        self.ab = AnnotationBbox(self.imagebox, [finalx, finaly], frameon=False)
        self.matplotlibwidget.axis.add_artist(self.ab)
        self.draw()
        self.custom_xlb = float(finalx - float(self.bombwidth) / 2)
        self.custom_ylb = float(finaly - float(self.bomblength) / 2)

    # Disconnect the bomb ids
    def _disconnect(self):
        'disconnect all the stored connection ids'
        self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidpress)
        self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidrelease)
        self.matplotlibwidget.figure.canvas.mpl_disconnect(self.cidmotion)

    def draw_defend_network(self):
        self.canvas = 1
        self.reset()
        self.Start_2.setEnabled(True)
        self.ShowResult.setEnabled(False)
        self.Original_2.setEnabled(False)
        self.bombwidth, self.bomblength = self.bombwidthDF.value(), self.bomblengthDF.value()
        self.Make_Random_Point(self.NumOfNodes_Defend.value())
        xydata_b = self.b_1.get_offsets()
        Graph_DF = nx.Graph()
        Graph_DF.add_nodes_from([i for i in range(len(xydata_b))])
        self.directed = self.DirectedDF.isChecked()
        if not self.directed:
            pos = dict()
            for i in range(len(Graph_DF.nodes)):
                pos[i] = (xydata_b[i][0], xydata_b[i][1])
            nx.set_node_attributes(Graph_DF, pos, 'pos')
            self.G = Graph_DF
        else:
            G_directed = nx.DiGraph()
            G_directed.add_nodes_from(Graph_DF)
            pos = dict()
            for i in range(len(G_directed.nodes)):
                pos[i] = (xydata_b[i][0], xydata_b[i][1])
            nx.set_node_attributes(G_directed, pos, 'pos')
            self.G = G_directed
        self.canvas = 1
        self.draw()
        self.edge_number.setText(str(self.NumOfNodes_Defend.value() + 2))
        self.edge_length.setText(str((self.NumOfNodes_Defend.value() + 2) * 5))
        self.Drag_2.setEnabled(True)
        self.Color_2.setEnabled(True)
        self.hoverconnect = self.matplotlibwidget_1.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover)  # Connect to hover highlight

    def defend_start(self):
        self.bartool_switch(False)
        self.Start_2.setEnabled(False)
        self.Confirm_2.setEnabled(True)
        # self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.hoverconnect)
        self.cidpress = self.matplotlibwidget_1.canvas.mpl_connect('button_press_event', self.on_click)
        self.cidrelease = self.matplotlibwidget_1.canvas.mpl_connect('button_release_event', self.off_click)


    # def add_or_remove_point(self, event):
    #     global b, _VARS
    #     xydata_b = self.b_1.get_offsets()
    #     xdata_b, ydata_b = self.b_1.get_offsets()[:, 0], self.b_1.get_offsets()[:, 1]
    #     accept_thresh = 0.5
    #     x, y = event.xdata, event.ydata
    #     if (not event.inaxes in self.matplotlibwidget_1.figure.axes) or (not self.accept_point(x, y, accept_thresh)):
    #         return
    #     x, y = x, y
    #     new_xydata_point_b = np.array([x, y])
    #     exist = False
    #     for i in range(len(xdata_b)):
    #         if xdata_b[i] == x and ydata_b[i] == y:
    #             exist = True
    #             break
    #     if event.button == 1:
    #         if not exist:
    #             new_xydata_b = np.insert(xydata_b, 0, new_xydata_point_b, axis=0)
    #             self.b_1.set_offsets(new_xydata_b)
    #             self.G.add_nodes_from([(len(new_xydata_b),{'pos':(x,y)})])
    #             self.matplotlibwidget_1.canvas.draw()
    #     elif event.button == 3:
    #         if exist:
    #             arr = np.where(xydata_b == np.array([float(x), float(y)]), 1, 0)
    #             index = 0
    #             for i in range(len(arr)):
    #                 if 0 not in arr[i]:
    #                     index = i
    #             new_xydata_b = np.delete(xydata_b, index, axis=0)
    #             self.b_1.set_offsets(new_xydata_b)
    #             newG = nx.Graph()
    #             newG.add_nodes_from([i for i in range(len(new_xydata_b))])
    #             pos = dict()
    #             for i in range(len(newG.nodes)):
    #                 pos[i] = (xydata_b[i][0], xydata_b[i][1])
    #             nx.set_node_attributes(newG, pos, 'pos')
    #             self.G = newG
    #             self.matplotlibwidget_1.canvas.draw()

    # Helper function for drawing edges
    def on_click(self, event):
        if event.button is MouseButton.LEFT:
            self.matplotlibwidget_1.figure.canvas.mpl_disconnect(self.hoverconnect)
            self.start = True
            self.binding_id = self.matplotlibwidget_1.canvas.mpl_connect('motion_notify_event', self.on_move)
            x, y = event.xdata, event.ydata
            pos = nx.get_node_attributes(self.G, 'pos')
            for i in pos:
                if x + 0.2 >= pos[i][0] >= x - 0.2 and y + 0.2 >= pos[i][1] >= y - 0.2:
                    self.s = i

    # Helper function for drawing edges
    def on_move(self, event):
        # get the x and y pixel coords
        pos = nx.get_node_attributes(self.G, 'pos')
        if not event.inaxes in self.matplotlibwidget_1.figure.axes:
            return
        x, y = event.xdata, event.ydata
        if x != pos[self.s][0] or y != pos[self.s][1]:
            self.moved = True
            if self.directed:
                tmp = self.matplotlibwidget_1.axis.get_children()

                if (not self.start) and self.last_arrow in tmp:
                    index = tmp.index(self.last_arrow)
                    tmp[index].remove()

                self.last_arrow = self.matplotlibwidget_1.axis.arrow(pos[self.s][0], pos[self.s][1],
                                                                     x - pos[self.s][0],
                                                                     y - pos[self.s][1],
                                                                     width=0.02, head_width=0.12,
                                                                     length_includes_head=True,
                                                                     zorder=2, fc='grey', ec='grey')
            else:
                if not self.start and self.matplotlibwidget_1.axis.lines:
                    self.matplotlibwidget_1.axis.lines.remove(self.matplotlibwidget_1.axis.lines[-1])
                self.matplotlibwidget_1.axis.plot(np.array([pos[self.s][0], x]),
                                                  np.array([pos[self.s][1], y]),
                                                  color="grey", zorder=1)
            self.start = False
            self.matplotlibwidget_1.canvas.draw()
        elif x == pos[self.s][0] or y == pos[self.s][1]:
            self.moved = False

    # Helper function for drawing edges
    def off_click(self, event):
        if event.button is MouseButton.LEFT:
            x, y = event.xdata, event.ydata
            pos = nx.get_node_attributes(self.G, 'pos')
            if self.moved:
                for i in pos:
                    if x + 0.2 >= pos[i][0] >= x - 0.2 and y + 0.2 >= pos[i][1] >= y - 0.2:
                        x, y = pos[i][0], pos[i][1]
                if self.directed:
                    tmp = self.matplotlibwidget_1.axis.get_children()
                    if (not self.start) and self.last_arrow in tmp:
                        index = tmp.index(self.last_arrow)
                        tmp[index].remove()
                    self.last_arrow = self.matplotlibwidget_1.axis.arrow(pos[self.s][0], pos[self.s][1],
                                                                         x - pos[self.s][0],
                                                                         y - pos[self.s][1],
                                                                         width=0.02, head_width=0.12,
                                                                         length_includes_head=True,
                                                                         zorder=2, fc='grey', ec='grey')
                else:
                    if not self.start and self.matplotlibwidget_1.axis.lines:
                        self.matplotlibwidget_1.axis.lines.remove(self.matplotlibwidget_1.axis.lines[-1])
                    self.matplotlibwidget_1.axis.plot(np.array([pos[self.s][0], x]),
                                                      np.array([pos[self.s][1], y]),
                                                      color="grey", zorder=1)
                x, y = event.xdata, event.ydata
                found = False
                dest = -1
                for i in pos:
                    if x + 0.2 >= pos[i][0] >= x - 0.2 and y + 0.2 >= pos[i][1] >= y - 0.2:
                        found = True
                        dest = i
                        break

                self.start = True
                self.moved = False

                tmp1 = int(self.edge_number.toPlainText()) - 1
                tmp2 = float(self.edge_length.toPlainText()) - np.sqrt(np.square(float(pos[self.s][0]) - x) \
                                                                       + np.square(float(pos[self.s][1]) - y))
                if tmp1 < 0 or tmp2 < 0 or not found or (self.s, dest) in self.G.edges or \
                        ((dest, self.s) in self.G.edges and not self.directed):
                    if self.directed:
                        arrow = self.matplotlibwidget_1.axis.get_children()
                        if self.last_arrow in arrow:
                            index = arrow.index(self.last_arrow)
                            arrow[index].remove()
                    else:
                        if self.matplotlibwidget_1.axis.lines:
                            self.matplotlibwidget_1.axis.lines.remove(self.matplotlibwidget_1.axis.lines[-1])
                    if tmp1 < 0 or tmp2 < 0:
                        mesBox = QMessageBox()
                        mesBox.setText("Out of Budget")
                        mesBox.exec_()
                    else:
                        mesBox = QMessageBox()
                        mesBox.setText("Illegal edge")
                        mesBox.exec_()
                else:
                    self.edge_number.setText(str(tmp1))
                    self.edge_length.setText(str(round(tmp2, 2)))
                    self.G.add_edge(self.s, dest)
                self.draw()

            self.matplotlibwidget_1.canvas.mpl_disconnect(self.binding_id)
        self.hoverconnect = self.matplotlibwidget_1.figure.canvas.mpl_connect(
            'motion_notify_event', self.hover)  # Connect to hover highlight

if __name__ == '__main__':
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    app = QApplication(sys.argv)
    w = MainWidget()
    w.show()
    sys.exit(app.exec_())
