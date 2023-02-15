class Compiler():
    def __init__(self) -> None:
        self.varCount = 0
        self.intVars = []
        self.floatVars = []
        self.strVars = []
        self.divOrMod = {"/":"mflo","%":"mfhi","*":"mflo"}
        self.addOrSub = {"+":"add","-":"sub"}
        self.multOrDiv = {"*":"mult","/":"div","%":"div"}
        self.temps = ["$t0","$t1","$t2","$t3","$t4","$t5","$t6","$t7"]
        self.tempsInd = 0
        self.bufferCounter = 0
        self.totalMipsData = []
        self.totalMipsCode = []

    #at the begining of compilation this function checks 
    # for any syntax error in the entire c++ code
    def syntaxCorrect(self):
        return True
    
    #our main compiler and operation assigner to each handlers
    def compile(self):
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
                self.totalMipsCode.append(code)
                self.totalMipsData.append(data)

            elif line.startswith("cin"):
                code, data = self.handleInput(line)
                self.totalMipsCode.append(code)
                self.totalMipsData.append(data)
            #we only handle comments that start at line start
            elif line.startswith("//"):
                code = self.handleComments(line)
                self.totalMipsCode.append([code])

            #we store integers and floats in temporary registers and strings 
            #in a memory location
            elif line.startswith("int"):
                if "+" in line or "-" in line:
                    code, data = self.handleAddorSub(line)
                    self.totalMipsCode.append(code)
                    self.totalMipsData.append(data)

                elif "*" in line or "/" in line or "%" in line:
                    code,data = self.handleMultOrDiv(line)
                    self.totalMipsCode.append(code)
                    self.totalMipsData.append(data)

                else:
                    data = self.handleIntVar(line)
                    self.totalMipsData.append(data)


            elif line.startswith("string"):
                data = self.handleStrVar(line)
                self.totalMipsData.append(data)

            elif line.startswith("float") or line.startswith("double"):
                data = self.handleFloatVar(line)
                self.totalMipsData.append(data)


            elif line == "":
                pass
            
            else:
                if "=" in line:
                    items = line.split()
                    if items[0] in self.intVars:
                        line = "int " + line
                        if "+" in line or "-" in line:
                            code, data = self.handleAddorSub(line)
                            self.totalMipsCode.append(code)
                            self.totalMipsData.append(data)

                            dataStr = data[0]
                            dataSplitted = dataStr.split()
                            dataSplitted[-1] = "0"
                            dataStr = " ".join(dataSplitted)
                            self.totalMipsData.remove([dataStr])
                            

                        elif "*" in line or "/" in line or "%" in line:
                            code,data = self.handleMultOrDiv(line)
                            self.totalMipsCode.append(code)
                            self.totalMipsData.append(data)


                            dataStr = data[0]
                            dataSplitted = dataStr.split()
                            dataSplitted[-1] = "0"
                            dataStr = " ".join(dataSplitted)
                            self.totalMipsData.remove([dataStr])
                            

                        else:
                            data = self.handleIntVar(line)
                            self.totalMipsData.append(data)


                            dataStr = data[0]
                            dataSplitted = dataStr.split()
                            dataSplitted[-1] = "0"
                            dataStr = " ".join(dataSplitted)
                            self.totalMipsData.remove([dataStr])
                            

                    elif items[0] in self.strVars:
                        line = "string " + line
                        data = self.handleStrVar(line)
                        self.totalMipsData.append(data)

                        dataStr = data[0]
                        dataSplitted = dataStr.split()
                        dataSplitted[-1] = ""
                        dataStr = " ".join(dataSplitted)
                        self.totalMipsData.remove([dataStr])

                    elif items[0] in self.floatVars:
                        line = "float " + line 
                        data = self.handleFloatVar(line)
                        self.totalMipsData.append(data)

                        dataStr = data[0]
                        dataSplitted = dataStr.split()
                        dataSplitted[-1] = "0.0"
                        dataStr = " ".join(dataSplitted)
                        self.totalMipsData.remove([dataStr])
                        
        return self.totalMipsCode,self.totalMipsData
    
    #this brave handler here is called whenever a cout(print) operation is needed 
    #and strong young man here handles it like a pro and returns only the result 
    #as data and code separately
    def handlePrint(self,line):
        printableWord = line[8:-1] 
        variablName = "var"+str(self.varCount)
        self.varCount += 1

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

        return mipsCode,mipsData
    
    def handleInput(self,line):
        code = []
        data = []
        items = line.split()
        varName = items[-1]
        if varName[-1] == ";":
            varName = varName[:-1]

        if varName in  self.intVars:
            #the input is integer
            code.append("li $v0,5")
            code.append("syscall")
            code.append(f"sw $v0,{varName}")

        elif varName in  self.strVars:
            #the input is integer
            tmp = varName+": .asciiz "
            self.totalMipsData.remove([tmp])
            data.append(f"{varName}: .space 256")
            code.append("li $v0,8")
            code.append(f"la $a0,{varName}")
            code.append("li $a1, 256")
            code.append("syscall")


        elif varName in  self.floatVars:
            #the input is integer
            code.append("li $f12,6")
            code.append("syscall")
            code.append(f"sf $f12,{varName}")

        return code,data
    
    #we are gon handle comments
    def handleComments(self,line):
        return ""
    
    #we gon handle variable assignments starting from int
    def handleIntVar(self,line):
        items = line.split()
        if "=" not in line:
            value = 0
            varName = items[1]
            
        else:
            value = items[3][:-1]
            varName = items[1]

        if varName[-1] == ";":
                        varName = varName[:-1]
        data = []

        #the following line maps the varible name to the register storing the number
        self.intVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .word {value}")
        return data

    def handleFloatVar(self,line):
        items = line.split()
        if "=" not in line:
            value = 0.0
            varName = items[1]

        else:
            value = items[3][:-1]
            varName = items[1]

        if varName[-1] == ";":
            varName = varName[:-1]

        data = []

        #the following line maps the varible name to the value
        self.floatVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .float {value}")
        return data
    
    def handleStrVar(self,line):
        items = line.split()

        if "=" not in line:
            value = ""
            varName = items[1]
            
        else:
            value = items[3][:-1]
            varName = items[1]

        if varName[-1] == ";":
            varName = varName[:-1]

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
        data = []

        if operand_2[-1]==";":
            operand_2 = operand_2[:-1]


        if (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) or (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
            operation += "i"

            if (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and not (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
                print("wrong order of operands literal value preceded variable")
                print(f"error on line {self.lines.index(line)+3}")


            elif (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
 
                code.append(f"addi $t0, $zero, {operand_1}")    # load the immediate value 5 into register $t0
                code.append(f"addi $t1, $zero, {operand_2}")    # load the immediate value 7 into register $t1
                code.append(f"{operation[:-1]} $t2, $t0, $t1")     # add the contents of $t0 and $t1 and store the result in $t2
                code.append(f"sw $t2,{resHolder}")
                self.intVars.append(resHolder)
                data.append(f"{resHolder}: .word 0")

                return code,data
        
        code.append(f"lw $t0,{operand_1}")

        if operation[-1] == "i":
            code.append(f"li $t1,{operand_2}")
            operation = operation[:-1]

        else:
            code.append(f"lw $t1,{operand_2}")

        code.append(f"{operation} $t2,$t0,$t1")
        code.append(f"sw $t2,{resHolder}")
        self.intVars.append(resHolder)
        data.append(f"{resHolder}: .word 0")

        return code,data
    

    #we gon handle multiplication now
    
    def handleMultOrDiv(self,line):
        items = line.split()
        productHolder = items[1]
        operator = items[4]
        operand_1 = items[3]
        operand_2 = items[5]
        code = []
        data = []
        
        if operand_1[-1] == ";":
            operand_1 = operand_1[:-1]

        if operand_2[-1] == ";":
            operand_2 = operand_2[:-1]


        #handling multiplication of two immediates
        if (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):

            code.append(f"li $t0,{operand_1}")
            code.append(f"li $t1,{operand_2}")
            code.append(f"{self.multOrDiv[operator]} $t0,$t1")
            code.append(f"{self.divOrMod[operator]} $t2")
            self.intVars.append(productHolder)
            code.append(f"sw $t2, {productHolder}")
            data.append(f"{productHolder}: .word 0")

            return code,data
        
        elif (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and not (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):
            code.append(f"li $t0,{operand_1}")
            code.append(f"lw $t1,{operand_2}")
            code.append(f"{self.multOrDiv[operator]} $t0,$t1")
            code.append(f"{self.divOrMod[operator]} $t2")
            self.intVars.append(productHolder)
            code.append(f"sw $t2, {productHolder}")
            data.append(f"{productHolder}: .word 0")

            return code,data
        
        elif not (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):

            code.append(f"lw $t0,{operand_1}")
            code.append(f"li $t1,{operand_2}")
            code.append(f"{self.multOrDiv[operator]} $t0,$t1")
            code.append(f"{self.divOrMod[operator]} $t2")
            self.intVars.append(productHolder)
            code.append(f"sw $t2, {productHolder}")
            data.append(f"{productHolder}: .word 0")

            return code,data
        
        elif not (ord(operand_1[0]) > 47 and ord(operand_1[0]) <58) and not (ord(operand_2[0]) > 47 and ord(operand_2[0]) <58):

            code.append(f"lw $t0,{operand_1}")
            code.append(f"lw $t1,{operand_2}")
            code.append(f"{self.multOrDiv[operator]} $t0,$t1")
            code.append(f"{self.divOrMod[operator]} $t2")
            self.intVars.append(productHolder)
            code.append(f"sw $t2, {productHolder}")
            data.append(f"{productHolder}: .word 0")

            return code,data


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
