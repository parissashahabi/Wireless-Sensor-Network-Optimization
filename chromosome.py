import random
import util
class Chromosome:
    def __init__(self, map_size, mut_prob, recomb_prob, max_BW, blocks_population, user_satisfaction_scores, user_satisfaction_levels, 
                tower_construction_cost, tower_maintanance_cost):
        # List of towers: (x, y, BW)
        self.towers = []

        # Indicates each neighborhood is connected to which tower
        self.adj_id = [[-1 for i in range(map_size)] for j in range(map_size)]

        # Mutation probability
        self.mut_prob = mut_prob

        # Recombination probability
        self.recomb_prob = recomb_prob

        # The maximum bandwidth of the towers
        self.max_BW = max_BW
        
        self.map_size = map_size
        self.blocks_population = blocks_population
        self.user_satisfaction_scores = user_satisfaction_scores
        self.user_satisfaction_levels = user_satisfaction_levels
        self.tower_construction_cost = tower_construction_cost
        self.tower_maintanance_cost = tower_maintanance_cost
        self.block_user_satisfaction_score = [[0 for i in range(map_size)] for j in range(map_size)]
        self.fitness = 0
        self.init_chromosome()
        
        
        
    def init_chromosome(self):
        num_tower = random.randint(1, self.map_size ** 2)
        for _ in range(num_tower):
            x = min(random.randint(0, 19) + random.random(), 19)
            y = min(random.randint(0, 19) + random.random(), 19)
            bw = random.gauss(0,self.max_BW)
            bw = min(self.max_BW,max(bw,0))
            tower = (x, y, bw)
            self.towers.append(tower)
        #print(f"nt= {len(self.towers)}")

        for i in range(self.map_size):
            for j in range(self.map_size):
                self.adj_id[i][j] = random.randint(0, len(self.towers)-1)
        self.calculate_fitness()
             
    def mut_append(self):
        append_prob = random.uniform(0,1)
        if append_prob <= self.mut_prob:
            x = min(random.randint(0,19) + random.random(),19)
            y = min(random.randint(0,19) + random.random(),19)
            bw = random.gauss(0,self.max_BW)
            bw = min(self.max_BW,max(bw,0))
            self.towers.append((x,y,bw))
            
    def mut_relocation(self):
        for i in range(self.map_size):
            for j in range(self.map_size):
                reloaction_prob = random.uniform(0,1)
                if reloaction_prob <= self.mut_prob:
                    self.adj_id[i][j] = random.randint(0,len(self.towers)-1)

    def mut_bandwidth(self):
        for tower_id in range(len(self.towers)):
            add_bandwidth_prob = random.uniform(0,1)
            if add_bandwidth_prob <= self.mut_prob:
                # Gaussian mutation
                added_bandwidth = random.gauss(0,self.max_BW)
                new_bandwidth = min(self.max_BW,max(self.towers[tower_id][2] + added_bandwidth,0))
                self.towers[tower_id] = (self.towers[tower_id][0],self.towers[tower_id][1],
                                          new_bandwidth)

    def mut_pop(self):
        pop_prob = random.uniform(0,1)
        if pop_prob <= self.mut_prob and len(self.towers) > 0:
            self.towers.pop()
            for i in range(self.map_size):
                for j in range(self.map_size):
                    if self.adj_id[i][j] == len(self.towers):
                        self.adj_id[i][j] = random.randint(0,max(len(self.towers)-1,0))

    def mutation(self):
        self.mut_append()
        self.mut_relocation()
        self.mut_bandwidth()
        self.mut_pop()
        self.calculate_fitness()

    def calculate_user_satisfaction_score(self, user_received_bandwidth):
        for i, user_satisfaction_level in enumerate(self.user_satisfaction_levels):
            if user_received_bandwidth < user_satisfaction_level:
                if i == 0:
                    return 0
                return self.user_satisfaction_scores[i-1]
            
        return self.user_satisfaction_scores[len(self.user_satisfaction_levels)-1]
        
    def calculate_tower_blocks_population(self, tower_id):
        tower_blocks_population = 0
        for r in range(len(self.adj_id)):
                for c in range(len(self.adj_id[r])):
                    if self.adj_id[r][c] == tower_id:
                        tower_blocks_population += self.blocks_population[r][c]
        return tower_blocks_population

    def calculate_fitness(self):
        users_satisfaction = 0
        for i in range(len(self.adj_id)):
            for j in range(len(self.adj_id[i])):
                block_population = self.blocks_population[i][j]
                tower_id = self.adj_id[i][j]
                if tower_id == -1 or tower_id >= len(self.towers):
                    continue
                #print(f"tower_id ={tower_id}")
        
                tower = self.towers[tower_id]
                tower_blocks_population = self.calculate_tower_blocks_population(tower_id)
                BW_prime = (tower[2] * block_population) / tower_blocks_population
                BW = util.coverage(tower, i, j) * BW_prime

                #  Calculate user's satisfaction
                self.block_user_satisfaction_score[i][j] = self.calculate_user_satisfaction_score(BW / block_population)
                users_satisfaction += (self.block_user_satisfaction_score[i][j] * block_population)
    
        # Calculate towers cost
        towers_cost = len(self.towers) * self.tower_construction_cost

        for tower in self.towers:
            towers_cost += (self.tower_maintanance_cost * tower[2])
        
        # Normalize 
        users_satisfaction_norm = users_satisfaction / ((self.map_size ** 2) * max(map(max, self.blocks_population)) * self.user_satisfaction_scores[-1])
        towers_cost_norm = 0
        if towers_cost != 0:
            towers_cost_norm = towers_cost / ((self.max_BW * len(self.towers) * self.tower_maintanance_cost) + towers_cost)
       

        # Maximization
        self.fitness = users_satisfaction_norm - towers_cost_norm
        #print(f"tower cost norm = {towers_cost_norm}, user norm = {users_satisfaction_norm}, fitness ={self.fitness}\n")

