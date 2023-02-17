import re

class Compiler():
    def __init__(self,file) -> None:
        self.fileToCompile = file
        self.varCount = 0
        self.intVars = []
        self.floatVars = []
        self.strVars = []
        self.divOrMod = {"/":"mflo","%":"mfhi","*":"mflo"}
        self.addOrSub = {"+":"add","-":"sub"}
        self.multOrDiv = {"*":"mult","/":"div","%":"div"}
        self.conditions = {"==":"bne","!=":"beq",">":"ble","<":"bge",">=":"blt","<=":"bgt"}
        self.bufferCounter = 0
        self.totalMipsData = []
        self.totalMipsCode = [["main:"]]
        self.loopCounter = 1
        self.blockCounter = 1
        self.mainflow_num = 0

        self.savedIndex = 0
        self.savedRegs = ["$s0","$s1","$s2","$s3","$s4","$s5","$s6","$s7"]
        self.bool_map = {
    '&&':'and',
    '||':'or',
    '!':'not'
    }

        self.set_on_map = {
        '<':'slt',
        '>':'sgt',
        '==':'seq', 
        '!=':'sne',
        '<=':'sle',
        '>=':'sge',
    }

        self.branch_created =[]#flag to check occurence of if statements :::> [True,...] if branches made else [] #supports nesting
        self.branches = {}#branches >>> label: body
        self.branch_num = 0

    #at the begining of compilation this function checks 
    # for any syntax error in the entire c++ code
    def syntaxCorrect(self):
        return True    
    
    #our main compiler and operation assigner to each handlers
    def compile(self,custom=False,lines=[]):
        
        if not custom:
            self.lines = []
            # Open a file in read mode
            with open(self.fileToCompile, 'r') as inputFile:
                # Iterate over each line in the inputFile
                for line in inputFile:
                    # self.Process the line (e.g. print it)
                    self.lines.append(line.strip())

            self.totalMipsData.append(['newLine: .asciiz "\\n"'])

        else:
            
            self.lines = lines

        #now we can do anything we want
        index = 0
        while index < len(self.lines):
            line = self.lines[index]
            if self.branch_created and not line.startswith("else") and line != "" and not custom:
                print("...",line,custom)
                self.branch_created.pop()
                mainflow = "mainflow" + str(self.mainflow_num) + ":"
                self.mainflow_num += 1
                self.totalMipsCode.append([mainflow])

            if line.startswith("cout"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                code,data = self.handlePrint(line)
                #if there is any error code is false and data contains error message
                if code == False:
                    return False,data
                
                self.totalMipsCode.append(code)
                self.totalMipsCode.append(["li $v0,4",'la $a0,newLine',"syscall"])
                self.totalMipsData.append(data)

            elif line.startswith("cin"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                code, data = self.handleInput(line)
                #if there is any error code is false and data contains error message
                if code == False:
                    return False,data
                
                self.totalMipsCode.append(code)
                self.totalMipsData.append(data)

            elif line.startswith("for"):
                #we gon handle the loop here
                result,msg =  self.checkSemicolon(line,2)

                if result == False:
                    return False, msg

                tmpIndex = index
                stack = None
                while tmpIndex < len(self.lines):

                    tmpLine = self.lines[tmpIndex]
                    for ch in tmpLine:
                        if ch == "{":
                            if not stack:
                                stack = 1

                            else:
                                stack += 1
                        
                        if ch == "}":
                            stack -= 1

                    if stack == 0:
                        lineEnd = tmpIndex
                        break
                    tmpIndex += 1

                
                tmpIndex = index
                code = []
                data = []

                currentLoop = "loop" + str(self.loopCounter)
                self.loopCounter += 1

                currentBlock = "block" + str(self.blockCounter)
                self.blockCounter += 1

                #statement 1
                tmpLine = self.lines[tmpIndex]
                start,end = tmpLine.index("("), tmpLine.index(";")
                tmpIndex += 2
                startOfBlock = tmpIndex
 
                stat_1 = tmpLine[start+1:end+1]
                codee,dataa = self.handleIntVar(stat_1)
                #if there is any error code is false and data contains error message
                if codee == False:
                    return False,dataa

                data += dataa
                varName = stat_1.split()[1]
                code.append(f"lw $t0,{varName}")
                code.append(f"{currentLoop}:")

                #lets handle statement 2 or the condition
                if "==" in tmpLine:
                    operator = self.conditions["=="]

                    terminatorValue = tmpLine[tmpLine.index("==")+2:]
                    if terminatorValue[0] == " ":
                        terminatorValue = terminatorValue[1:]
                    
                    terminatorValue = terminatorValue[:terminatorValue.index(";")]

                elif "!=" in tmpLine:
                    operator = self.conditions["!="]

                    terminatorValue = tmpLine[tmpLine.index("!")+2:]
                    if terminatorValue[0] == " ":
                        terminatorValue = terminatorValue[1:]
                    
                    terminatorValue = terminatorValue[:terminatorValue.index(";")]

                elif ">=" in tmpLine:
                    operator = self.conditions[">="]

                    terminatorValue = tmpLine[tmpLine.index(">")+2:]
                    if terminatorValue[0] == " ":
                        terminatorValue = terminatorValue[1:]
                    
                    terminatorValue = terminatorValue[:terminatorValue.index(";")]


                elif "<=" in tmpLine:
                    operator = self.conditions["<="]

                    terminatorValue = tmpLine[tmpLine.index("<=")+2:]
                    if terminatorValue[0] == " ":
                        terminatorValue = terminatorValue[1:]
                    
                    terminatorValue = terminatorValue[:terminatorValue.index(";")]


                elif "<" in tmpLine:
                    operator = self.conditions["<"]

                    terminatorValue = tmpLine[tmpLine.index("<")+1:]
                    if terminatorValue[0] == " ":
                        terminatorValue = terminatorValue[1:]
                    
                    terminatorValue = terminatorValue[:terminatorValue.index(";")]


                elif ">" in tmpLine:
                    operator = self.conditions[">"]

                    terminatorValue = tmpLine[tmpLine.index(">")+1:]
                    if terminatorValue[0] == " ":
                        terminatorValue = terminatorValue[1:]
                    
                    terminatorValue = terminatorValue[:terminatorValue.index(";")]

                currentLoopEnd = currentLoop+"end"
                code.append(f"{operator} $t0,{terminatorValue},{currentLoopEnd}")

                code.append(f"jal {currentBlock}")
                #at the end operations
                #we gon handle statement 3
                if "++" in tmpLine:
                    code.append("addi $t0,$t0,1")

                elif "+" in tmpLine:
                    indS = tmpLine.index("+")
                    indE = tmpLine.index(")")
                    incVal = tmpLine[indS+1:indE]
                    if "=" in incVal:
                        incVal = incVal[1:]

                    if incVal[0] == " ":
                        incVal = incVal[1:]

                    if incVal[-1] == " ":
                        incVal = incVal[:-1]

                    code.append(f"addi $t0,$t0,{incVal}")    

                elif "--" in tmpLine:
                    code.append("subi $t0,$t0,1")

                elif "-" in tmpLine:
                    indS = tmpLine.index("-")
                    indE = tmpLine.index(")")
                    incVal = tmpLine[indS+1:indE]
                    if "=" in incVal:
                        incVal = incVal[1:]

                    if incVal[0] == " ":
                        incVal = incVal[1:]

                    if incVal[-1] == " ":
                        incVal = incVal[:-1]

                    code.append(f"subi $t0,$t0,{incVal}")                        

                code.append(f"sw $t0,{varName}")
                code.append(f"j {currentLoop}")

                #handle the block here
                code.append("")
                endOfBlock = lineEnd-1
                self.totalMipsCode.append(code)
                self.totalMipsData.append(data)
                self.handleBlock(startOfBlock,endOfBlock,currentBlock) #inclusive for both sides
                #here we specify a label for the loop to come to execute the rest of the code when its done with the loop
                
                index = lineEnd

            #we only handle comments that start at line start
            elif line.startswith("//"):
                code = self.handleComments(line)
                self.totalMipsCode.append([code])

            elif line.startswith("if") or line.startswith("else"):
                print("line",line)
                currIndex, code,data = self.conditionHandler(line,index)
                index = currIndex
                self.totalMipsCode.append(code)
                self.totalMipsData.append(data)
                print(code,data)

            elif line.startswith("int"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                if "+" in line or "-" in line:
                    code, data = self.handleAddorSub(line)
                    #if there is any error code is false and data contains error message
                    if code == False:
                        return False,data
                    
                    self.totalMipsCode.append(code)
                    self.totalMipsData.append(data)

                elif "*" in line or "/" in line or "%" in line:
                    code,data = self.handleMultOrDiv(line)
                    #if there is any error code is false and data contains error message
                    if code == False:
                        return False,data
                    
                    self.totalMipsCode.append(code)
                    self.totalMipsData.append(data)

                else:
                    code,data = self.handleIntVar(line)
                    #if there is any error code is false and data contains error message
                    if code == False:
                        return False,data
                    
                    self.totalMipsData.append(data)


            elif line.startswith("string"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                code, data = self.handleStrVar(line)
                #if there is any error code is false and data contains error message
                if code == False:
                    return False,data

                self.totalMipsData.append(data)

            elif line.startswith("float") or line.startswith("double"):
                code, data = self.handleFloatVar(line)
                #if there is any error code is false and data contains error message
                if code == False:
                    return False,data

                self.totalMipsData.append(data)


            elif line == "" or line.startswith("namespace") or line.startswith("#include"):
                pass
                            
            else:
                if "=" in line:
                    result,msg =  self.checkSemicolon(line,1)
                    if result == False:
                        return False, msg
                    
                    items = line.split()
                    if items[0] in self.intVars:
                        line = "int " + line
                        if "+" in line or "-" in line:
                            code, data = self.handleAddorSub(line)
                            #if there is any error code is false and data contains error message
                            if code == False:
                                return False,data
                            
                            self.totalMipsCode.append(code)
                            self.totalMipsData.append(data)

                            dataStr = data[0]
                            dataSplitted = dataStr.split()
                            dataSplitted[-1] = "0"
                            dataStr = " ".join(dataSplitted)
                            self.totalMipsData.remove([dataStr])
                            

                        elif "*" in line or "/" in line or "%" in line:
                            code,data = self.handleMultOrDiv(line)
                            #if there is any error code is false and data contains error message
                            if code == False:
                                return False,data
                            
                            self.totalMipsCode.append(code)
                            self.totalMipsData.append(data)


                            dataStr = data[0]
                            dataSplitted = dataStr.split()
                            dataSplitted[-1] = "0"
                            dataStr = " ".join(dataSplitted)
                            self.totalMipsData.remove([dataStr])
                            

                        else:
                            code, data = self.handleIntVar(line)
                            #if there is any error code is false and data contains error message
                            if code == False:
                                return False,data
                            
                            self.totalMipsData.append(data)


                            dataStr = data[0]
                            dataSplitted = dataStr.split()
                            dataSplitted[-1] = "0"
                            dataStr = " ".join(dataSplitted)
                            self.totalMipsData.remove([dataStr])
                            

                    elif items[0] in self.strVars:
                        line = "string " + line
                        code, data = self.handleStrVar(line)
                        #if there is any error code is false and data contains error message
                        if code == False:
                            return False,data
                        
                        self.totalMipsData.append(data)

                        dataStr = data[0]
                        dataSplitted = dataStr.split()
                        dataSplitted[-1] = ""
                        dataStr = " ".join(dataSplitted)
                        self.totalMipsData.remove([dataStr])

                    elif items[0] in self.floatVars:
                        line = "float " + line 
                        code,data = self.handleFloatVar(line)
                        #if there is any error code is false and data contains error message
                        if code == False:
                            return False,data
                        
                        self.totalMipsData.append(data)

                        dataStr = data[0]
                        dataSplitted[-1] = "0.0"
                        dataStr = " ".join(dataSplitted)
                        self.totalMipsData.remove([dataStr])

                    else:
                        return False, f"Unknown variable {items[0]} on line number {self.lines.index(line)}"
                    

                elif line.startswith("{") or line.startswith("}"):
                    pass

                else:
                    if line in self.lines:
                        return False,"Syntax error on line " + str(self.lines.index(line)+1)

                    else:
                        return False, "Syntax error"

            index += 1

        if not custom:
            for key, val in self.branches.items():
                st,en,name,mainflow = val

                start_index = len(self.totalMipsCode)
                self.handleBlock(st,en,name,True)
                self.totalMipsCode.append([f"j {mainflow}"])
                current_index = len(self.totalMipsCode)

                branches = self.totalMipsCode[start_index:current_index]
                self.totalMipsCode = branches + self.totalMipsCode[:start_index]

            self.totalMipsCode = [["j main"]] + self.totalMipsCode

                

                
        return self.totalMipsCode,self.totalMipsData
    
    #we gon define a function that checks for simicolons
    def checkSemicolon(self,line,numOfSemicolons):
        semiColonCount = line.count(';')

        if semiColonCount < numOfSemicolons and line in self.lines:
            return False, "Missing semicolon on line " + str(self.lines.index(line)+1)
        
        elif semiColonCount > numOfSemicolons and line in self.lines:
            return False, "Extra semicolon on line " + str(self.lines.index(line)+1)
        
        return True,""
          
    
    #this brave handler here is called whenever a cout(print) operation is needed 
    #and strong young man here handles it like a pro and returns only the result 
    #as data and code separately
    def handlePrint(self,line):
        printableWord = line[8:-1] 
        variablName = "var"+str(self.varCount)
        self.varCount += 1

        if printableWord == "":
            return False,f"Syntax error on line {self.lines.index(line)}"

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
            #the input is string
            tmp = varName+": .asciiz "
            self.totalMipsData.remove([tmp])
            data.append(f"{varName}: .space 256")
            code.append("li $v0,8")
            code.append(f"la $a0,{varName}")
            code.append("li $a1, 256")
            code.append("syscall")


        elif varName in  self.floatVars:
            #the input is float
            code.append("li $v0,6")
            code.append("syscall")
            code.append(f"swc1 $f0,{varName}")

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
        code = []

        #the following line maps the varible name to the register storing the number
        self.intVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .word {value}")
        return code, data

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
        code = []

        #the following line maps the varible name to the value
        self.floatVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .float {value}")
        return code, data
    
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
        code = []

        #the following line maps the varible name to the value
        self.strVars.append(varName)

        #now we store the number
        data.append(f"{varName}: .asciiz {value}")
        return code, data
    
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
                print(f"error on line {self.lines.index(line)+1}")


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
        


    def handleBlock(self,start,end,currentBlock,isCond=False,label=True):
        lines = []

        originalLines = self.lines
        blockDeclaration = currentBlock + ":"

        print(start,end)
        print(originalLines)
        for i in range(start,end+1):
            lines.append(originalLines[i])

        if label:
            self.totalMipsCode.append([blockDeclaration])

        self.compile(True,lines)

        if not isCond:
            self.totalMipsCode.append(["jr $ra"])
            self.totalMipsCode.append([f"loop{currentBlock[-1]}end:"])

        self.lines = originalLines




    def isVariable(self,term):
        if term and term[0].isnumeric(): return False
        elif term.replace('_', '').isalnum(): return True
        return False


    def logicalOperation(self,exp):
        output = []

        if len(exp) == 3:
            op, left_exp, right_exp = exp
            subOutput_1 = self.equality_op(left_exp)
            subOutput_2 = self.equality_op(right_exp)

            output.extend(subOutput_1)
            output.extend(subOutput_2)

            output.append(f"{self.bool_map[op]} {self.savedRegs[self.savedIndex]}, {self.savedRegs[self.savedIndex - 1]}, {self.savedRegs[self.savedIndex - 2]}")
            self.savedIndex += 1

        else:
            subOutput = self.equality_op(exp[1])
            output.extend(subOutput)

            output.append(f'{self.bool_map[exp[0]]} {self.savedRegs[self.savedIndex]}, {self.savedRegs[self.savedIndex - 1]}')
            savedIndex += 1

        return output



    def equality_op(self,expression):
        
        left, right = 0, len(expression) - 1
        while left < len(expression) and expression[left].isalnum() or expression[left] == '_':  
            left += 1

        while right > -1 and expression[right].isalnum() or expression[right] == '_':
            right -= 1

        arg1 = expression[:left]
        equality_op = expression[left: right + 1]
        arg2 = expression[right + 1:]
        
        output = []
        
        if self.isVariable(arg1):
            output.append(f'lw $t1, {arg1}')
        elif arg1.isnumeric():
            output.append(f'addi $t1, $zero, {arg1}') 
        if arg2.isnumeric():
            output.append(f'addi $t2, $zero, {arg2}') 

        elif self.isVariable(arg2):
            output.append(f'lw $t2, {arg2}')


        if equality_op in self.set_on_map:
            output.append(f'{self.set_on_map[equality_op]} {self.savedRegs[self.savedIndex]} $t1, $t2')
            self.savedIndex += 1

        return output
            

    def boolHandle(self,exp):
        exp = exp.replace(' ', '')

        if '&&' in exp:
            exp = exp.split('&&')

            formal = ['&&']
            formal.extend(exp)

            return self.logicalOperation(formal)
        
        elif '||' in exp:
            exp = exp.split('||')

            formal = ['||']
            formal.extend(exp)

            return self.logicalOperation(formal)

        elif exp.startswith('!'):
            exp = exp.split('(')

            exp[-1] = exp[-1][:-1]
            return self.logicalOperation(exp)

        else:
            return self.equality_op(exp)
        

    def process(self,line):
        return ["..."],['data']



    def conditionHandler(self,line,currIndex):
        self.branch_created.append(True)
        code = data = []

        if line.startswith('if') or line.startswith('else if'):
        
            start = line.find('(')
            par_stack = ['(']
            condition = ''
            i = start + 1

            while i < len(line) and par_stack:

                if line[i] == ')':
                    par_stack.pop()

                elif line[i] == '(':
                    par_stack.append('(')

                else:
                    condition += line[i]
                
                i += 1


            condition_assembly = self.boolHandle(condition)
            code = condition_assembly

            code.append(f'bnez {self.savedRegs[self.savedIndex - 1]}, branch{self.branch_num}')
            
            ################################################
            tmpIndex = currIndex
            stack = None
            while tmpIndex < len(self.lines):

                tmpLine = self.lines[tmpIndex]
                for ch in tmpLine:
                    if ch == "{":
                        if not stack:
                            stack = 1

                        else:
                            stack += 1
                    
                    if ch == "}":
                        stack -= 1

                if stack == 0:
                    lineEnd = tmpIndex
                    break
                tmpIndex += 1
            
            startInd = currIndex + 2
            endInd = lineEnd-1
            ################################################

            currBranch = f'branch{self.branch_num}'
            self.branches[currBranch] = (startInd,endInd,currBranch,"mainflow"+str(self.mainflow_num))
            self.branch_num += 1
            print(self.branches)
            return lineEnd,code, data
        
        else:
            tmpIndex = currIndex
            stack = None

            while tmpIndex < len(self.lines):

                tmpLine = self.lines[tmpIndex]
                for ch in tmpLine:
                    if ch == "{":
                        if not stack:
                            stack = 1

                        else:
                            stack += 1
                    
                    if ch == "}":
                        stack -= 1

                if stack == 0:
                    lineEnd = tmpIndex
                    break
                tmpIndex += 1
            
            startInd = currIndex + 2
            endInd = lineEnd-1
            self.handleBlock(startInd,endInd,"",True,False)

            return lineEnd,code,data






#this is not going to be changed from now on
#all we are gon go from now on is adding all the other 
#operation handlers and call them wherever they are needed

def main(inputFile,outputFile):
    compiler = Compiler(inputFile)
    res = compiler.syntaxCorrect()

    if res == True:
        code,data = compiler.compile()

        if code == False:
            return data
        
        # Open a file in write mode
        with open(outputFile, 'w') as result:
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

        return True

    else:
        return res

################################# here comes the GUI ########################################################

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Compiler")
        self.pack(expand=True, fill='both')
        self.create_widgets()
        self.editor.insert(tk.END, "//=============== C++ code ===============\n")
        self.output.insert(tk.END, "#=============== Mips Assembly ===============\n")


    def create_widgets(self):
        # Text Editor with line numbers
        editor_frame = tk.Frame(self)
        editor_frame.pack(side='left', expand=True, fill='both')

        self.linenumbers = tk.Text(editor_frame, width=2, height=25, bg="#060e20", fg="gray", font=("Consolas", 12), padx=10, pady=7, border=0)
        self.linenumbers.pack(side='left', fill='y')
        self.linenumbers.insert('end', '1\n', 'line')
        self.linenumbers.config(state='disabled')#070e21
        self.editor = tk.Text(editor_frame, width=80, height=25, bg='#161e30', fg='#ffffff',
                            insertbackground='white', selectbackground='gray', selectforeground='white',
                            font=("Consolas", 12), border=0, padx=7, pady=7)
                            
        self.editor.pack(side='left', expand=True, fill='both')
        self.editor.tag_configure("line", background="black", foreground='gray')
        self.editor.bind("<Key>", self.update_line_numbers)
        self.scrollbar = tk.Scrollbar(editor_frame, command=self.editor.yview, border=0 , width=10)
        self.scrollbar.pack(side='right', fill='y')
    
        self.editor.config(yscrollcommand=self.scrollbar.set)


        # Buttons
        button_frame = tk.Frame(self, bg='#161e30', border=0)
        button_frame.pack(side='top', anchor='ne')

        self.open_button = tk.Button(button_frame, text="Open", command=self.open_file, bg="#408560", fg="#FFFFFF",font=("Consolas",12), border=0)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Save", command=self.save_file, bg="#408560", fg="#FFFFFF",font=("Consolas",12), border=0)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_editor, bg='gray', fg='white',font=("Consolas",13), border=0)
        self.clear_button.pack(side='right', padx=5, pady=5)

        self.run_button = tk.Button(button_frame, text="Compile", command=self.run_compiler, bg='#43bb57', fg='white',font=("Consolas",13), border=0)
        self.run_button.pack(side='right', padx=5, pady=5)

        self.copy_button = tk.Button(button_frame, text="Copy", command=self.copy_output, bg='#435799', fg='white',font=("Consolas",11), border=0)
        self.copy_button.pack(side=tk.LEFT, padx=20, pady=1)

        # Output area
        self.output = tk.Text(self, width=80, height=50, bg='#030715', fg='white', insertbackground='white',
                            font=("Consolas", 12), border=0, padx=10, pady=10)
        self.output.pack(side='bottom', fill='x')

        # Set the remaining space to be black
        self.config(bg='#161e30')

        

    def copy_output(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.output.get("1.0", "end"))


    def update_line_numbers(self, event):
        self.linenumbers.config(state='normal')
        self.linenumbers.delete(1.0, tk.END)
        text = self.editor.get(1.0, tk.END)
        lines = text.count("\n")
        for i in range(1, lines+1):
            self.linenumbers.insert(tk.END, f"{i}\n", "line")
        self.linenumbers.config(state='disabled')

    def run_compiler(self):
        #first we load the contents of the editor to an input file
        with open("input.txt", "w") as f:
            f.write(self.editor.get("1.0", "end"))
            
        # TODO: Implement your compiler logic here
        self.output.delete(1.0, tk.END)
        
        #then we do the compiling
        result = main('input.txt','output.txt')
        if result == True:
            #and finally we out put the mips code 
            with open('output.txt', 'r') as result:
                for line in result:
                    self.output.insert(tk.END, line)

        else:
            self.output.insert(tk.END,result)

        

        

    def clear_editor(self):
        self.editor.delete(1.0, tk.END)
        self.output.delete(1.0, tk.END)
        self.linenumbers.config(state='normal')
        self.linenumbers.delete(1.0, tk.END)
        self.linenumbers.insert('end', '1\n', 'line')
        self.linenumbers.config(state='disabled')

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Open File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.editor.delete("1.0", tk.END)
            with open(file_path, "r") as f:
                text = f.read()
                self.editor.insert("1.0", text)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(title="Save File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                text = self.editor.get("1.0", tk.END)
                f.write(text)


root = tk.Tk()
root.configure(bg='black')
app = Application(master=root)
app.mainloop()