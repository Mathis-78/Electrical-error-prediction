import math
import functions
import random

class Node:
    def __init__(self, node_id, params):
        self.id = node_id
        self.params = params

        self.failed = False
        self.temp = params['T_amb']
        self.age = 0.0
        self.load = 0.0
        self.neighbors_influence = 0.0
        self.prev_temp = params['T_amb']
        self.prev_age = 0.0

    def update_physics(self, time, neighbors_failed_count, neighbors_temp_avg, neighbors_count):
        self.neighbors_influence = (1/neighbors_count)*neighbors_failed_count
        current_noise = random.uniform(-self.params["epsilon"], self.params["epsilon"])
        self.load = (self.params["A"]*math.sin(self.params["omega"]*time)+self.params["B"])* (1+self.params["k_report"]*self.neighbors_influence)+current_noise
        if self.load < 0: self.load = 0
        self.prev_temp = self.temp
        self.temp = self.prev_temp + self.params["a_joule"]*(self.load**2) - self.params["b_cool"] * (self.prev_temp - self.params["T_amb"]) + self.params["c_diff"] * neighbors_count*(neighbors_temp_avg-self.prev_temp)
        self.prev_age = self.age
        self.age = self.prev_age + math.exp((self.params["E_a"]/8.617e-5)*(1/(self.params["T_ref"]+273.15)-1/(self.temp+273.15)))

    def check_failure(self):
        if not self.failed:

            normalized_load = self.load / 100.0
            normalized_age = min(self.age / self.params["A_max"], 1.0)
            normalized_temp = min(self.temp / self.params["T_max"], 1.0)

            risk = self.params["w_neighbor"]*self.neighbors_influence + self.params["w_load"] * normalized_load +self.params["w_temp"]* normalized_temp+ self.params["w_age"] * normalized_age
            self.failed = True if random.random() < functions.sigmoid(risk, self.params["threshold"],k=5.0) else False