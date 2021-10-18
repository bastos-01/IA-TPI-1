from tree_search import *
from cidades import *
from strips import *


class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth'): 
        super().__init__(problem,strategy)

    def hybrid1_add_to_open(self,lnewnodes):
        #first add the nodes in even positions 
        self.open_nodes[:0] = list(filter(lambda x: lnewnodes.index(x)%2 == 0, lnewnodes[::-1]))
        #then add the nodes in odd positions
        self.open_nodes += list(filter(lambda x: lnewnodes.index(x)%2 != 0, lnewnodes))

    def hybrid2_add_to_open(self,lnewnodes):
        #extend the new nodes
        self.open_nodes.extend(lnewnodes)
        #sort all nodes (depth - offset)
        self.open_nodes.sort(key = lambda node: node.depth - node.offset)

    def search2(self):
        #setting the atributes depth and offset
        self.root.depth = 0
        self.root.offset = 0
        offsets = {} #list to count offsets
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.terminal = len(self.open_nodes)+1
                self.solution = node
                return self.get_path(node)
            self.non_terminal+=1
            node.children = []
            #only set to 0 in the first node 
            if(node.depth not in offsets.keys()):
                offsets[node.depth] = 0
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                if newstate not in self.get_path(node):
                    newnode = SearchNode(newstate,node)
                    newnode.depth = node.depth + 1
                    newnode.offset = offsets[node.depth] #setting current offset to new node
                    offsets[node.depth] += 1 #incrementing the offset 
                    node.children.append(newnode)
            self.add_to_open(node.children)
        return None



    def search_from_middle(self):
        #creating the tree from inicial state to middle state
        self.from_init = MyTree(SearchProblem(self.problem.domain, self.problem.initial, self.problem.domain.middle(self.problem.initial, self.problem.goal))) 
        #creating the tree from middle state to goal state
        self.to_goal = MyTree(SearchProblem(self.problem.domain, self.problem.domain.middle(self.problem.initial, self.problem.goal), self.problem.goal))
        return self.from_init.search2()[:-1] + self.to_goal.search2() #[:-1] to avoid repetition of the middle state 


class MinhasCidades(Cidades):

    # state that minimizes heuristic(state1,middle)+heuristic(middle,state2)
    def middle(self,city1,city2):
        #list comprehention that calculates the sum of the 2 heuristics and stores it in a dictionary for each city
        heurDic = {curr_city:(self.heuristic(city1, curr_city) + self.heuristic(curr_city, city2)) for curr_city in self.coordinates if(curr_city != city2 and curr_city != city1)}
        return list({k:v for k, v in sorted(heurDic.items(), key = lambda heurDic: heurDic[1])}.keys())[0] #sorts the dictionary by the heuristic value and returns the first one

class MySTRIPS(STRIPS):
    def result(self, state, action):
        # validate pre conditions
        if all(pre_cond in state for pre_cond in action.pc):
            #negative effects 
            newstate = [p for p in state if p not in action.neg]
            #positive effects
            newstate.extend(action.pos)
            return newstate
        # if pre conditions do not validate
        return None

    def sort(self,state):
        #ording by alphabetic order
        ording = lambda list: sorted([str(a) for a in list])
        return ording(state)


