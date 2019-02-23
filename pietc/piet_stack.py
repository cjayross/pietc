class Stack(list):
    def pop(self):
        return self.pop()
    def push(self, item):
        self.append(item)
    def add(self):
        self.push(self.pop()+self.pop())
    def subtract(self):
        first = self.pop()
        second = self.pop()
        self.push(second-first)
    def multiply(self):
        self.push(self.pop()*self.pop())
    def divide(self):
        first = self.pop()
        second = self.pop()
        if first == 0:
            print("dividing by 0!")
            self.push(second)
            self.push(first)
        self.push(second/first)
    def mod(self):
        first = self.pop()
        second = self.pop()
        self.push(second%first)
    def invert(self):
        self[-1] = 1 if self[-1] == 0 else 1
    def greater(self):
        first = self.pop()
        second = self.pop()
        self.push(int(second > first))
    # def pointer(self):
        # used in program flow
    # def switch(self):
        # used in program flow
    def duplicate(self):
        self.push(self[-1])
    def roll(self):
        #cycle the first |second| amount of elements |first| amount of times 
        first = self.pop()
        second = self.pop()
        for i in range(0,first):
            temp = self.pop()
            self.insert(-(second-1),temp) # -1 since we popped something