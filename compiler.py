class Compiler():
    def __init__(self) -> None:
        self.varCount = 0
        self.intVars = []
        self.floatVars = []
        self.strVars = []
        self.savedVars = {}
        self.savedRegs = ["$s0","$s1","$s2","$s3","$s4","$s5","$s6","$s7"]
        self.savedIndex = 0
        self.addOrSub = {"+":"add","-":"sub"}

    #at the begining of compilation this function checks 
    # for any syntax error in the entire c++ code
    def syntaxCorrect(self):
        return True
    
    #our main compiler and operation assigner to each handlers
    def compile(self):
        totalMipsCode = []
        totalMipsData = []
        self.lines = []

        # Open a file in read mode
        with open('cppToCompile.cpp', 'r') as inputFile:
            # Iterate over each line in the inputFile
            for line in inputFile:
                # Process the line (e.g. print it)
                self.lines.append(line.strip())

        self.lines.pop(0)
        self.lines.pop(0)

        #now we can do anything we want
        for line in self.lines:
            if line.startswith("cout"):
                code,data = self.handlePrint(line)
                totalMipsCode.append(code)
                totalMipsData.append(data)

            #we only handle comments that start at line start
            elif line.startswith("//"):
                code = self.handleComments(line)
                totalMipsCode.append([code])

            #we store integers and floats in temporary registers and strings 
            #in a memory location
            elif line.startswith("int"):
                if "=" in line:
                    if "+" in line or "-" in line:
                        code = self.handleAddorSub(line)
                        totalMipsCode.append(code)

                    else:
                        data = self.handleIntVar(line)
                        totalMipsData.append(data)

            elif line.startswith("string"):
                data = self.handleStrVar(line)
                totalMipsData.append(data)

            elif line.startswith("float") or line.startswith("double"):
                data = self.handleFloatVar(line)
                totalMipsData.append(data)


            elif line == "":
                pass
            
        return totalMipsCode,totalMipsData
    
    #this brave handler here is called whenever a cout(print) operation is needed 
    #and strong young man here handles it like a pro and returns only the result 
    #as data and code separately
    def handlePrint(self,line):
        printableWord = line[8:-1] 
        variablName = "var"+str(self.varCount)
        
        #we have to differentiate the data type here
        
        if printableWord.startswith('"'):
            mipsCode = ["li $v0,4","la $a0 "+variablName,"syscall"]
            mipsData = [variablName+f': .asciiz {printableWord}']

        else:
            mipsCode = mipsData = []
            if printableWord and ord(printableWord[0]) > 47 and ord(printableWord[0]) < 58:
                mipsCode = ["li $v0,1","li $a0,"+printableWord,"syscall"]
                mipsData = []

            else:
                if printableWord in self.intVars:
                    mipsCode = ["li $v0,1","lw $a0,"+printableWord,"syscall"]
                    mipsData = []
                    

                elif printableWord in self.strVars:
                    mipsCode = ["li $v0,4","la $a0,"+printableWord,"syscall"]
                    mipsData = []

                elif printableWord in self.floatVars:
                    mipsCode = ["li $v0,2","lwc1 $f12,"+printableWord,"syscall"]
                    mipsData = []

                elif printableWord in self.savedVars:
                    register = self.savedVars[printableWord]
                    mipsCode = ["li $v0,1",f"move $a0,{register}","syscall"]

        self.varCount += 1

        return mipsCode,mipsData
    
    #we are gon handle comments
    def handleComments(self,line):
        comment = "#" + line[2:]
        return comment
    
    #we gon handle variable assignments starting from int
    def handleIntVar(self,line):
        items = line.split()
        value = items[3][:-1]
        varName = items[1]
        data = []

        #the following line maps the varible name to the register storing the number
        self.intVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .word {value}")
        return data
    
    def handleFloatVar(self,line):
        items = line.split()
        value = items[3][:-1]
        varName = items[1]
        data = []

        #the following line maps the varible name to the value
        self.floatVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .float {value}")
        return data
    
    def handleStrVar(self,line):
        items = line.split()
        value = items[3][:-1]
        varName = items[1]
        data = []

        #the following line maps the varible name to the value
        self.strVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .asciiz {value}")
        return data
    
    def handleAddorSub(self,line):
        items = line.split()

        operand = items[4]
        resHolder = items[1]
        operand_1 = items[3]
        operand_2 = items[5]
        operation = self.addOrSub[operand]
        code = []
        if operand_2[-1]==";":
            operand_2 = operand_2[:-1]


        if (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) or (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
            operation += "i"

            if (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and not (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
                print("wrong order of operands literal value preceded variable")
                print(f"error on line {self.lines.index(line)+3}")


            elif (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
                currentFreeRegister = self.savedRegs[self.savedIndex]
                self.savedVars[resHolder] = currentFreeRegister
 
                code.append(f"addi $t0, $zero, {operand_1}")    # load the immediate value 5 into register $t0
                code.append(f"addi $t1, $zero, {operand_2}")    # load the immediate value 7 into register $t1
                code.append(f"{operation[:-1]} {currentFreeRegister}, $t0, $t1")     # add the contents of $t0 and $t1 and store the result in $t2
                self.savedIndex += 1    

                return code
        
        currentFreeRegister = self.savedRegs[self.savedIndex]
        self.savedVars[resHolder] = currentFreeRegister
        code.append(f"lw $t1,{operand_1}")
        t2 = "$t2"

        if operation[-1] == "i":
            t2 = operand_2

        else:
            code.append(f"lw $t2,{operand_2}")

        code.append(f'{operation} {currentFreeRegister},$t1,{t2}')
        self.savedIndex += 1    

        return code
        




#this is not going to be changed from now on
#all we are gon go from now on is adding all the other 
#operation handlers and call them wherever they are needed

def main():
    compiler = Compiler()
    if compiler.syntaxCorrect():
        code,data = compiler.compile()

        # Open a file in write mode
        with open('result.txt', 'w') as result:
            # Write each line to the result
            result.write(".text \n")
            for lines in code:
                for line in lines:
                    result.write("\t"+line+"\n")
                result.write("\n")

            result.write(".data \n")
            for lines in data:
                for line in lines:
                    result.write("\t"+line+"\n")
                result.write("\n")

    else:
        print("Syntax Error")

main()
