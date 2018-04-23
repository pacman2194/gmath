#!/usr/bin/python

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import askokcancel
from tkinter.ttk import Notebook
from tkinter.ttk import Style
import pickle
from graph import Graph
from flow import Flow

class App(tk.Frame):
    def __init__(self, master):
        #graph object and changed variable to keep track of save-state
        self.graphObj = Graph()
        self.flowObj = Flow()
        self.changed = []

        #get the application window, set title and basic attributes
        tk.Frame.__init__(self, master, background="#1d1d1d")
        self.pack()
        self.master.title("gmath")
        self.master.resizable(True, True)
        self.master.tk_setPalette(background="#222222", foreground="#2ecc71")

        #basic universal behaviors
        #if window closed by window manager, exit safely
        self.master.protocol("WM_DELETE_WINDOW", self.click_exit)
        
        #set of keybindings
        self.master.bind("<Control_L><Escape>", self.click_exit)
        self.master.bind("<Control_L>1", self.dependent_active)
        self.master.bind("<Control_L>2", self.dependency_active)
        self.master.bind("<Control_L>a", self.add_button_active)
        self.master.bind("<Control_L>t", self.top_sort_button_active)
        self.master.bind("<Control_L>3", self.vertex_active)
        self.master.bind("<Alt_L>1", self.arc_node_active)
        self.master.bind("<Alt_L>2", self.arc_neighbor_active)
        self.master.bind("<Alt_L>3", self.arc_capacity_active)
        self.master.bind("<Alt_L>4", self.node_active)
        self.master.bind("<Control_L>A", self.add_vertex_active)
        self.master.bind("<Control_L>R", self.remove_vertex_active)
        self.master.bind("<Control_L>r", self.remove_button_active)
        self.master.bind("<Control_L>s", self.menu_save)
        self.master.bind("<Control_L>o", self.menu_open)
        self.master.bind("<Control_L>f", self.flow_tab_active)
        self.master.bind("<Control_L>d", self.dep_tab_active)

        #Menu bar
        menubar = tk.Menu(self, background="#1d1d1d", foreground="#2ecc71")

        #File menu in menu bar: open, save, exit
        filemenu = tk.Menu(menubar, tearoff=0, background="#1d1d1d", foreground="#2ecc71")
        filemenu.add_command(label="Open", command=self.menu_open)
        filemenu.add_command(label="Save", command=self.menu_save)
        filemenu.add_separator()
        filemenu.add_command(label="Exit Ctrl+Esc", command=self.click_exit)
        menubar.add_cascade(label="File", menu=filemenu)

        #slap the menubar altogether
        self.master.config(menu=menubar)

        #tab panes and ttk styling for notebook
        self.style = Style()
        self.style.theme_create( "gmath", parent="alt", settings={
        "TNotebook": {"configure": {"background": "#1d1d1d" } },
        "TNotebook.Tab": {
            "configure": {"background": "#1d1d1d", "foreground": "#2ecc71", "padding": [4, 2] },
            "map":       {"background": [("selected", "#222222")] } }} )
        self.style.theme_use("gmath")
        self.tabs = Notebook(self)
        self.tabs.pack()

        #dependency graph frame inside notebook
        dep_graph_frame = tk.Frame(self.tabs)
        dep_graph_frame.pack()

        #manipulation frame in dependency graph frame
        manipulation_frame = tk.Frame(dep_graph_frame, borderwidth=0)
        manipulation_frame.pack(padx=0, pady=10)

        #edge frame in manipulation frame
        #contains dependent and dependency labels and entries and
        #add and remove buttons for edges
        edge_frame = tk.Frame(manipulation_frame, borderwidth=0)
        edge_frame.pack(padx=15, pady=15, side="left")
        dependent_frame = tk.Frame(edge_frame, borderwidth=0)
        dependent_frame.pack()
        dependency_frame = tk.Frame(edge_frame, borderwidth=0)
        dependency_frame.pack()
        tk.Label(dependent_frame, text="Dependent:  ").pack(side="left")
        tk.Label(dependency_frame, text="Dependency:").pack(side="left")
        self.dependent_entry = tk.Entry(dependent_frame)
        self.dependent_entry.pack(pady=5, side="left")
        self.dependent_entry.focus_set()
        self.dependency_entry = tk.Entry(dependency_frame)
        self.dependency_entry.pack(pady=5, side="left")
        self.add_button = tk.Button(edge_frame, text="Add Edge", command=self.add_edge)
        self.add_button.bind("<Return>",self.add_edge)
        self.add_button.pack(side="left")
        self.remove_button = tk.Button(edge_frame, text="Remove Edge", command=self.remove_edge)
        self.remove_button.bind("<Return>",self.remove_edge)
        self.remove_button.pack(side="left")
        self.remove_button['state'] = 'disabled'

        #vertex frame in manipulation frame
        #contains a label and entry for vertex and 
        #add and remove buttons for the vertex
        vertex_frame = tk.Frame(manipulation_frame, borderwidth=0)
        vertex_frame.pack(padx=15, pady=15, side="left")
        vertex_entry_frame = tk.Frame(vertex_frame, borderwidth=0)
        vertex_entry_frame.pack()
        tk.Label(vertex_entry_frame, text="Vertex: ").pack(side="left")
        self.vertex_entry = tk.Entry(vertex_entry_frame)
        self.vertex_entry.pack(pady=5, side="left")
        vertex_button_frame = tk.Frame(vertex_frame, borderwidth=0)
        vertex_button_frame.pack()
        self.add_vertex_button = tk.Button(vertex_button_frame, text="Add Vertex", command=self.add_vertex)
        self.add_vertex_button.bind("<Return>",self.add_vertex)
        self.add_vertex_button.pack(side="left")
        self.remove_vertex_button = tk.Button(vertex_button_frame, text="Remove Vertex", command=self.remove_vertex)
        self.remove_vertex_button.bind("<Return>",self.remove_vertex)
        self.remove_vertex_button.pack(side="left")
        self.remove_vertex_button['state'] = 'disabled'

        #lists frame, contains listbox for edges and vertices
        lists_frame = tk.Frame(dep_graph_frame, borderwidth=0)
        lists_frame.pack(padx=15, pady=15)

        #edge list scrollable listbox
        edge_list_frame = tk.Frame(lists_frame, borderwidth=0)
        edge_list_frame.pack(side="left", padx=15)
        tk.Label(edge_list_frame, text="Edge List: ").pack(padx=5, pady=5)
        edge_scrollbar = tk.Scrollbar(edge_list_frame, orient="vertical")
        self.edge_list = tk.Listbox(edge_list_frame, selectmode='multiple', selectbackground="#2ecc71", selectforeground="#222222", yscrollcommand=edge_scrollbar.set, height=10, borderwidth=1)
        edge_scrollbar.config(command=self.edge_list.yview)
        edge_scrollbar.pack(side="right", fill="y")
        self.edge_list.bind("<Delete>", self.remove_edge_list)
        self.edge_list.pack(side="left", fill="y", expand=1)

        #vertex list scrollable listbox
        vertex_list_frame = tk.Frame(lists_frame, borderwidth=0)
        vertex_list_frame.pack(side="right", padx=15)
        tk.Label(vertex_list_frame, text="Vertex List: ").pack(padx=5, pady=5)
        vertex_scrollbar = tk.Scrollbar(vertex_list_frame, orient="vertical")
        self.vertex_list = tk.Listbox(vertex_list_frame, selectmode='multiple', selectbackground="#2ecc71", selectforeground="#222222", yscrollcommand=vertex_scrollbar.set, height=10, borderwidth=1)
        vertex_scrollbar.config(command=self.vertex_list.yview)
        vertex_scrollbar.pack(side="right", fill="y")
        self.vertex_list.bind("<Delete>", self.remove_vertex_list)
        self.vertex_list.pack(side="left", fill="y", expand=1)

        #function frame in dependency graph frame
        function_frame = tk.Frame(dep_graph_frame, borderwidth=0)
        function_frame.pack(padx=15, pady=15)

        #output frame in function frame
        output_frame = tk.Frame(function_frame, borderwidth=0)
        output_frame.pack()

        #basic outputs such as vertex count, edge count, and if cycle was detected
        basic_output_frame = tk.Frame(output_frame, borderwidth=0)
        basic_output_frame.pack(padx=15, pady=15, side="left")
        basic_output_vertices = tk.Frame(basic_output_frame, borderwidth=0)
        basic_output_vertices.pack()
        basic_output_edges = tk.Frame(basic_output_frame, borderwidth=0)
        basic_output_edges.pack()
        basic_output_cycle = tk.Frame(basic_output_frame, borderwidth=0)
        basic_output_cycle.pack()
        tk.Label(basic_output_vertices, text="Vertices: ").pack(padx=5, pady=5, side="left")
        self.vertices_label = tk.Label(basic_output_vertices, text="")
        self.vertices_label.pack(padx=10, pady=5, side="left")
        tk.Label(basic_output_edges, text="Edges: ").pack(padx=5, pady=5, side="left")
        self.edges_label = tk.Label(basic_output_edges, text="")
        self.edges_label.pack(padx=10, pady=5, side="left")
        tk.Label(basic_output_cycle, text="Cycle Detected: ").pack(padx=5, pady=5, side="left")
        self.cycle_label = tk.Label(basic_output_cycle, text="")
        self.cycle_label.pack(padx=10, pady=5, side="left")

        #topological sort frame with scrollable listbox and button to call top sort function
        output_top_sort_frame = tk.Frame(output_frame, borderwidth=0)
        output_top_sort_frame.pack(padx=15, pady=15, side="right")
        tk.Label(output_top_sort_frame, text="Topological Sort: ").pack(padx=5, pady=0)
        top_sort_list_frame = tk.Frame(output_top_sort_frame, borderwidth=0)
        top_sort_list_frame.pack(pady=15)
        top_sort_scrollbar = tk.Scrollbar(top_sort_list_frame, orient="vertical")
        self.top_sort_list = tk.Listbox(top_sort_list_frame, yscrollcommand=top_sort_scrollbar.set, height=10, borderwidth=1)
        top_sort_scrollbar.config(command=self.top_sort_list.yview)
        top_sort_scrollbar.pack(side="right", fill="y")
        self.top_sort_list.pack(side="left", fill="y", expand=1)
        self.top_sort_button = tk.Button(output_top_sort_frame, text="Topological Sort", command=self.topological_sort)
        self.top_sort_button.bind("<Return>",self.topological_sort)
        self.top_sort_button.pack()
        self.top_sort_button['state'] = 'disabled'


        #add dependency graph frame tab to the notebook tab frame
        self.tabs.add(dep_graph_frame, text="Dep Graph")

        #network flow frame
        flow_frame = tk.Frame(self.tabs)
        flow_frame.pack()
        
        #arc and node content containter
        arc_and_node_frame = tk.Frame(flow_frame, borderwidth=0)
        arc_and_node_frame.pack(padx=0, pady=10)

        #arc frame content
        arc_frame = tk.Frame(arc_and_node_frame, borderwidth=0)
        arc_frame.pack(padx=15, pady=15, side="left")
        arc_node_frame = tk.Frame(arc_frame, borderwidth=0)
        arc_node_frame.pack()
        arc_neighbor_frame = tk.Frame(arc_frame, borderwidth=0)
        arc_neighbor_frame.pack()
        arc_capacity_frame = tk.Frame(arc_frame, borderwidth=0)
        arc_capacity_frame.pack()
        tk.Label(arc_node_frame, text="Node:     ").pack(side="left")
        tk.Label(arc_neighbor_frame, text="Neighbor:").pack(side="left")
        tk.Label(arc_capacity_frame, text="Capacity:").pack(side="left")
        self.arc_node_entry = tk.Entry(arc_node_frame)
        self.arc_node_entry.pack(pady=5, side="left")
        self.arc_node_entry.focus_set()
        self.arc_neighbor_entry = tk.Entry(arc_neighbor_frame)
        self.arc_neighbor_entry.pack(pady=5, side="left")
        self.arc_capacity_entry = tk.Entry(arc_capacity_frame)
        self.arc_capacity_entry.pack(pady=5, side="left")
        self.add_arc_button = tk.Button(arc_frame, text="Add Edge", command=self.add_arc)
        self.add_arc_button.bind("<Return>",self.add_arc)
        self.add_arc_button.pack(side="left")
        self.remove_arc_button = tk.Button(arc_frame, text="Remove Edge", command=self.remove_arc)
        self.remove_arc_button.bind("<Return>",self.remove_arc)
        self.remove_arc_button.pack(side="left")
        self.remove_arc_button['state'] = 'disabled'

        #node frame content
        node_frame = tk.Frame(arc_and_node_frame, borderwidth=0)
        node_frame.pack(padx=15, pady=15, side="left")
        node_entry_frame = tk.Frame(node_frame, borderwidth=0)
        node_entry_frame.pack()
        tk.Label(node_entry_frame, text="Node: ").pack(side="left")
        self.node_entry = tk.Entry(node_entry_frame)
        self.node_entry.pack(pady=5, side="left")
        node_button_frame = tk.Frame(node_frame, borderwidth=0)
        node_button_frame.pack()
        self.add_node_button = tk.Button(node_button_frame, text="Add Node", command=self.add_node)
        self.add_node_button.bind("<Return>",self.add_node)
        self.add_node_button.pack(side="left")
        self.remove_node_button = tk.Button(node_button_frame, text="Remove Node", command=self.remove_node)
        self.remove_node_button.bind("<Return>",self.remove_node)
        self.remove_node_button.pack(side="left")
        self.remove_node_button['state'] = 'disabled'

        #lists frame, contains listbox for nodes and arcs
        flow_lists_frame = tk.Frame(flow_frame, borderwidth=0)
        flow_lists_frame.pack(padx=15, pady=15)

        #arc list scrollable listbox
        arc_list_frame = tk.Frame(flow_lists_frame, borderwidth=0)
        arc_list_frame.pack(side="left", padx=15)
        tk.Label(arc_list_frame, text="Arc List: ").pack(padx=5, pady=5)
        arc_scrollbar = tk.Scrollbar(arc_list_frame, orient="vertical")
        self.arc_list = tk.Listbox(arc_list_frame, selectmode='multiple', selectbackground="#2ecc71", selectforeground="#222222", yscrollcommand=edge_scrollbar.set, height=10, borderwidth=1)
        arc_scrollbar.config(command=self.arc_list.yview)
        arc_scrollbar.pack(side="right", fill="y")
        self.arc_list.bind("<Delete>", self.remove_arc_list)
        self.arc_list.pack(side="left", fill="y", expand=1)

        #node list scrollable listbox
        node_list_frame = tk.Frame(flow_lists_frame, borderwidth=0)
        node_list_frame.pack(side="right", padx=15)
        tk.Label(node_list_frame, text="Node List: ").pack(padx=5, pady=5)
        node_scrollbar = tk.Scrollbar(node_list_frame, orient="vertical")
        self.node_list = tk.Listbox(node_list_frame, selectmode='multiple', selectbackground="#2ecc71", selectforeground="#222222", yscrollcommand=vertex_scrollbar.set, height=10, borderwidth=1)
        node_scrollbar.config(command=self.node_list.yview)
        node_scrollbar.pack(side="right", fill="y")
        #self.node_list.bind("<Delete>", self.remove_node_list)
        self.node_list.pack(side="left", fill="y", expand=1)

        #flow output frame
        flow_output_frame = tk.Frame(flow_frame, borderwidth=0)
        flow_output_frame.pack(padx=15, pady=15)

        flow_output_nodes = tk.Frame(flow_output_frame, borderwidth=0)
        flow_output_nodes.pack()
        flow_output_arcs = tk.Frame(flow_output_frame, borderwidth=0)
        flow_output_arcs.pack()
        flow_output_max = tk.Frame(flow_output_frame, borderwidth=0)
        flow_output_max.pack()
        tk.Label(flow_output_nodes, text="Nodes: ").pack(padx=5, pady=5, side="left")
        self.nodes_label = tk.Label(flow_output_nodes, text="")
        self.nodes_label.pack(padx=10, pady=5, side="left")
        tk.Label(flow_output_arcs, text="Arcs: ").pack(padx=5, pady=5, side="left")
        self.arcs_label = tk.Label(flow_output_arcs, text="")
        self.arcs_label.pack(padx=10, pady=5, side="left")
        tk.Label(flow_output_max, text="Maximum Flow: ").pack(padx=5, pady=5, side="left")
        self.max_label = tk.Label(flow_output_max, text="")
        self.max_label.pack(padx=10, pady=5, side="left")

        self.tabs.add(flow_frame, text="Flow Graph")

        #update the geometry of the master frame
        self.master.geometry()
        self.master.update()

        #setup to put screen centered horizontally and starting at top third vertically
        x = int((self.master.winfo_screenwidth() - self.master.winfo_width()) / 2)
        y = int((self.master.winfo_screenheight() - self.master.winfo_height()) / 3)
        self.master.geometry("{}x{}+{}+{}".format(self.master.winfo_width(), self.master.winfo_height(), x, y))

    def add_edge(self, event=None):
        ''' simple add edge to graph '''
        dependency_text = self.dependency_entry.get()
        dependent_text = self.dependent_entry.get()
        if dependency_text != "" and dependent_text != "" and dependency_text != dependent_text:
            if self.graphObj.add_edge(dependent_text,dependency_text):
                self.vertex_list.delete(0, 'end')
                for e in self.graphObj.vertices():
                    self.vertex_list.insert(tk.END, str(e))
                if 'dpg' not in self.changed:
                    self.changed.append('dpg')
                self.dependency_entry.delete(0, 'end')
                self.dependent_entry.delete(0, 'end')
                self.graphObj.is_cyclic()
                self.edge_list.insert(tk.END, str(dependent_text)+" -> "+str(dependency_text))
                self.update_output_labels()
                self.change_button_state()

    def add_arc(self, event=None):
        '''  '''
        arc_node_text = self.arc_node_entry.get()
        arc_neighbor_text = self.arc_neighbor_entry.get()
        arc_capacity_text = self.arc_capacity_entry.get()
        if arc_node_text != '' and arc_neighbor_text != '' and arc_capacity_text.isnumeric() and float(arc_capacity_text) >= 0 and arc_node_text != arc_neighbor_text:
            self.flowObj.add_arc(arc_node_text, arc_neighbor_text, float(arc_capacity_text))
            self.update_flow_labels()
            self.node_list.delete(0, 'end')
            for e in self.flowObj.nodes():
                self.node_list.insert(tk.END, str(e))
            self.arc_list.insert(tk.END, str(arc_node_text)+" -("+str(arc_capacity_text)+")-> "+str(arc_neighbor_text))
            self.arc_node_entry.delete(0, 'end')
            self.arc_neighbor_entry.delete(0, 'end')
            self.arc_capacity_entry.delete(0, 'end')
            if 'flw' not in self.changed:
                self.changed.append('flw')
            self.change_button_state()
        
    def remove_edge(self, event=None):
        ''' simple remove edge from graph '''
        dependency_text = self.dependency_entry.get()
        dependent_text = self.dependent_entry.get()
        if dependency_text != "" and dependent_text != "":
            if self.graphObj.remove_edge(dependent_text,dependency_text):
                self.edge_list.delete(0, 'end')
                for e in self.graphObj.edges():
                    self.edge_list.insert(tk.END, str(e[0])+" -> "+str(e[1]))
                if 'dpg' not in self.changed:
                    self.changed.append('dpg')
                self.dependency_entry.delete(0, 'end')
                self.dependent_entry.delete(0, 'end')
                if not self.graphObj.is_cyclic():
                    self.topological_sort()
                self.update_output_labels()
                self.change_button_state()

    def remove_edge_list(self, event=None):
        ''' remove selected edges from edge list listbox '''
        selections = [self.edge_list.get(x).split("->") for x in self.edge_list.curselection()]
        #edge_sel = [x.strip() for x in "".split("->")]
        values = []
        for y in selections:
            values.append([y[0].strip(), y[1].strip()])
        for e in values:
            if self.graphObj.remove_edge(e[0], e[1]):
                if 'dpg' not in self.changed:
                    self.changed.append('dpg')
                self.graphObj.is_cyclic()
                self.update_output_labels()
                self.change_button_state()
        self.edge_list.delete(0, 'end')
        for e in self.graphObj.edges():
            self.edge_list.insert(tk.END, str(e[0])+" -> "+str(e[1]))
        if not self.graphObj.cycle_detected():
            self.topological_sort()

    def remove_arc(self, event=None):
        '''  '''
        arc_node_text = self.arc_node_entry.get()
        arc_neighbor_text = self.arc_neighbor_entry.get()
        if arc_node_text != '' and arc_neighbor_text != '':
            if self.flowObj.remove_arc(arc_node_text, arc_neighbor_text):
                self.update_flow_labels()
                if 'flw' not in self.changed:
                    self.changed.append('flw')
                self.arc_list.delete(0, 'end')
                for e in self.flowObj.arcs():
                    self.arc_list.insert(tk.END, str(e[0])+" -("+str(e[2])+")-> "+str(e[1]))
                self.arc_node_entry.delete(0, 'end')
                self.arc_neighbor_entry.delete(0, 'end')
                self.arc_capacity_entry.delete(0, 'end')
                self.change_button_state()

    def remove_arc_list(self, event=None):
        '''  '''
        selections = [self.arc_list.get(x).split("-") for x in self.arc_list.curselection()]
        print(selections)
        values = []
        for y in selections:
            values.append([y[0].strip(), y[2][1:].strip()])
        for e in values:
            if self.flowObj.remove_arc(e[0],e[1]):
                if 'flw' not in self.changed:
                    self.changed.append('flw')
                self.update_flow_labels()
                self.change_button_state()
                self.update_flow_lists()

    def add_vertex(self, event=None):
        ''' simple add vertex to graph '''
        vertex_text = self.vertex_entry.get()
        if vertex_text != "":
            if self.graphObj.add_vertex(vertex_text):
                self.vertex_list.insert(tk.END, str(vertex_text))
                if 'dpg' not in self.changed:
                    self.changed.append('dpg')
                self.vertex_entry.delete(0, 'end')
                self.update_output_labels()
                self.change_button_state()

    def add_node(self, event=None):
        '''  '''
        node_text = self.node_entry.get()
        if node_text != '':
            if self.flowObj.add_node(node_text):
                if 'flw' not in self.changed:
                    self.changed.append('flw')
                self.node_entry.delete(0, 'end')
                self.change_button_state()
                self.update_flow_labels()
                self.node_list.insert(tk.END, str(node_text))

    def remove_vertex(self, event=None):
        ''' simple remove vertex from graph '''
        vertex_text = self.vertex_entry.get()
        if vertex_text != "":
            if self.graphObj.remove_vertex(vertex_text):
                self.edge_list.delete(0, 'end')
                for e in self.graphObj.edges():
                    self.edge_list.insert(tk.END, str(e[0])+" -> "+str(e[1]))
                self.vertex_list.delete(0, 'end')
                for e in self.graphObj.vertices():
                    self.vertex_list.insert(tk.END, str(e))
                if 'dpg' not in self.changed:
                    self.changed.append('dpg')
                self.vertex_entry.delete(0, 'end')
                if not self.graphObj.is_cyclic():
                    self.topological_sort()
                self.update_output_labels()
                self.change_button_state()

    def remove_vertex_list(self, event=None):
        ''' removes all selected vertices from vertex listbox '''
        values = [self.vertex_list.get(x).strip() for x in self.vertex_list.curselection()]
        for v in values:
            if self.graphObj.remove_vertex(v):
                if 'dpg' not in self.changed:
                    self.changed.append('dpg')
                self.graphObj.is_cyclic()
                self.update_output_labels()
                self.change_button_state()
        self.edge_list.delete(0, 'end')
        for e in self.graphObj.edges():
            self.edge_list.insert(tk.END, str(e[0])+" -> "+str(e[1]))
        self.vertex_list.delete(0, 'end')
        for e in self.graphObj.vertices():
            self.vertex_list.insert(tk.END, str(e))
        if not self.graphObj.cycle_detected():
            self.topological_sort()

    def remove_node(self, event=None):
        '''  '''
        node_text = self.node_entry.get()
        if node_text != '':
            if self.flowObj.remove_node(node_text):
                self.update_flow_labels()
                if 'flw' not in self.changed:
                    self.changed.append('flw')
                self.node_entry.delete(0, 'end')
                self.change_button_state()
                self.update_flow_lists()

    def topological_sort(self):
        ''' outputs the topological sort in scrollable listbox in order '''
        if not self.graphObj.cycle_detected():
            self.top_sort_list.delete(0, 'end')
            for v in self.graphObj.topological_sort():
                self.top_sort_list.insert(tk.END, str(v))

    def click_exit(self, event=None):
        ''' exit program safely by asking if they want to save changes '''
        if len(self.changed) == 0:
            self.master.destroy()
        else:
            if 'dpg' in self.changed:
                graph_result = True
                while graph_result and 'dpg' in self.changed:
                    graph_result = askokcancel("Python","Would you like to save your changes to the dependency graph?")
                    if graph_result:
                        self.menu_save()
            if 'flw' in self.changed:
                graph_result = True
                while graph_result and 'flw' in self.changed:
                    graph_result = askokcancel("Python","Would you like to save your changes to the flow network?")
                    if graph_result:
                        self.menu_save()
            self.master.destroy()

    def menu_save(self, event=None):
        ''' opens a "save as" dialog to save the graph '''
        filename = asksaveasfilename(initialdir = ".",title = "Select file", filetypes=(("Dependency Graph", "*.dpg"),("Flow Network", "*.flw") ))
        try:
            with open(filename, 'wb') as output:
                if filename[-3:] == 'dpg':
                    pickle.dump(self.graphObj, output, pickle.HIGHEST_PROTOCOL)
                    self.changed.remove('dpg')
                elif filename[-3:] == 'flw':
                    pickle.dump(self.flowObj, output, pickle.HIGHEST_PROTOCOL)
                    self.changed.remove('flw')
                else:
                    raise
        except:
            print("Something went terribly wrong")

    def menu_open(self, event=None):
        ''' opens an "open file" dialog to open a graph file '''
        filename = askopenfilename(initialdir = ".",title = "Select file",filetypes=(("Dependency Graph", "*.dpg"),("Flow Network", "*.flw") ))
        try:
            if filename[-3:] == 'dpg' and 'dpg' in self.changed:
                result = askokcancel("Python","Would you like to save your changes to the dependency graph?")
                while result == True:
                    self.menu_save()
                    if 'dpg' in self.changed:
                        result = askokcancel("Python","Would you like to save your changes to the dependency graph?")
                    else:
                        result = False
            elif filename[-3:] == 'flw' and 'flw' in self.changed:
                result = askokcancel("Python","Would you like to save your changes to the flow network?")
                while result == True:
                    self.menu_save()
                    if 'flw' in self.changed:
                        result = askokcancel("Python","Would you like to save your changes to the flow network?")
                    else:
                        result = False
            with open(filename, 'rb') as inputf:
                if filename[-3:] == 'dpg':
                    self.graphObj = pickle.load(inputf)
                    self.update_output_labels()
                    self.change_button_state()
                    self.vertex_list.delete(0, 'end')
                    for e in self.graphObj.vertices():
                        self.vertex_list.insert(tk.END, str(e))
                    self.edge_list.delete(0, 'end')
                    for e in self.graphObj.edges():
                        self.edge_list.insert(tk.END, str(e[0])+" -> "+str(e[1]))
                    self.topological_sort()
                    if 'dpg' in self.changed:
                        self.changed.remove('dpg')
                elif filename[-3:] == 'flw':
                    self.flowObj = pickle.load(inputf)
                    self.update_flow_labels()
                    self.change_button_state()
                    self.update_flow_lists()
                    if 'flw' in self.changed:
                        self.changed.remove('flw')
        except:
            print("Something went terribly wrong")

    def update_flow_lists(self):
        self.node_list.delete(0, 'end')
        for e in self.flowObj.nodes():
            self.node_list.insert(tk.END, str(e))
        self.arc_list.delete(0, 'end')
        for e in self.flowObj.arcs():
            self.arc_list.insert(tk.END, str(e[0])+" -("+str(e[2])+")-> "+str(e[1]))

    def update_output_labels(self):
        ''' update the vertex and edge count labels and the cycle detected label '''
        self.vertices_label['text'] = str(self.graphObj.order())
        self.edges_label['text'] = str(self.graphObj.size())
        self.cycle_label['text'] = str(self.graphObj.cycle_detected())

    def update_flow_labels(self):
        ''' update arc and node count labels and max flow label '''
        self.nodes_label['text'] = str(self.flowObj.order())
        self.arcs_label['text'] = str(self.flowObj.size())
        mf = self.flowObj.max_flow()
        if mf != False:
            self.max_label['text'] = str(mf)
        else:
            self.max_label['text'] = 'Insufficient conditions'

    def change_button_state(self):
        ''' enable and disable buttons according to their ability to be used
            based on the current state of the graph
        '''
        if self.graphObj.order() > 0:
            self.top_sort_button['state'] = 'normal'
            self.remove_vertex_button['state'] = 'normal'
        else:
            self.top_sort_button['state'] = 'disabled'
            self.remove_vertex_button['state'] = 'disabled'
        if self.graphObj.size() > 0:
            self.remove_button['state'] = 'normal'
        else:
            self.remove_button['state'] = 'disabled'
        if self.flowObj.order() > 0:
            self.remove_node_button['state'] = 'normal'
        else:
            self.remove_node_button['state'] = 'disabled'
        if self.flowObj.size() > 0:
            self.remove_arc_button['state'] = 'normal'
        else:
            self.remove_arc_button['state'] = 'disabled'

    def dependency_active(self, event=None):
        ''' set dependency text entry field active '''
        self.dependency_entry.focus_set()

    def dependent_active(self, event=None):
        ''' set dependent text entry field active '''
        self.dependent_entry.focus_set()

    def arc_node_active(self, event=None):
        ''' set arc node text entry field active '''
        self.arc_node_entry.focus_set()

    def arc_neighbor_active(self, event=None):
        ''' set arc neighbor text entry field active '''
        self.arc_neighbor_entry.focus_set()

    def arc_capacity_active(self, event=None):
        ''' set arc capacity text entry field active '''
        self.arc_capacity_entry.focus_set()

    def add_button_active(self, event=None):
        ''' set add edge button active and add edge '''
        self.add_button.focus_set()
        self.add_edge()

    def remove_button_active(self, event=None):
        ''' set remove edge button active and remove edge '''
        self.remove_button.focus_set()
        self.remove_edge()

    def add_vertex_active(self, event=None):
        ''' set add vertex button active and add vertex '''
        self.add_vertex_button.focus_set()
        self.add_vertex()

    def remove_vertex_active(self, event=None):
        ''' set the remove vertex button active and call remove vertex '''
        self.remove_vertex_button.focus_set()
        self.remove_vertex()

    def vertex_active(self, event=None):
        ''' set the vertex entry field active '''
        self.vertex_entry.focus_set()

    def node_active(self, event=None):
        ''' set the node entry field active '''
        self.node_entry.focus_set()

    def top_sort_button_active(self, event=None):
        ''' set the topological sort button active and call topological sort '''
        self.top_sort_button.focus_set()
        self.topological_sort()

    def dep_tab_active(self, event=None):
        ''' show the dependency graph tab '''
        self.tabs.select(0)

    def flow_tab_active(self, event=None):
        ''' show the flow network tab '''
        self.tabs.select(1)

#start the magic
if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.mainloop()
