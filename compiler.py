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
        self.totalMipsCode = []
        self.loopCounter = 1
        self.blockCounter = 1

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
                    # Process the line (e.g. print it)
                    self.lines.append(line.strip())

            self.totalMipsData.append(['newLine: .asciiz "\\n"'])

        else:
            
            self.lines = lines

        #now we can do anything we want
        index = 0
        while index < len(self.lines):
            line = self.lines[index]

            if line.startswith("cout"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                code,data = self.handlePrint(line)
                self.totalMipsCode.append(code)
                self.totalMipsCode.append(["li $v0,4",'la $a0,newLine',"syscall"])
                self.totalMipsData.append(data)

            elif line.startswith("cin"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                code, data = self.handleInput(line)
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
                dataa = self.handleIntVar(stat_1)

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


                code.append(f"{operator} $t0,{terminatorValue},exit")

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

                
                index = lineEnd

            #we only handle comments that start at line start
            elif line.startswith("//"):
                code = self.handleComments(line)
                self.totalMipsCode.append([code])


            elif line.startswith("int"):
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
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
                result,msg =  self.checkSemicolon(line,1)
                if result == False:
                    return False, msg
                
                data = self.handleStrVar(line)
                self.totalMipsData.append(data)

            elif line.startswith("float") or line.startswith("double"):
                data = self.handleFloatVar(line)
                self.totalMipsData.append(data)


            elif line == "" or line.startswith("namespace") or line.startswith("include"):
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

                else:
                    if line in self.lines:
                        return False,"Syntax error on line " + str(self.lines.index(line)+1)

                    else:
                        return False, "Syntax error"
                
            index += 1
                        
        if not custom:
            #implementing an exit function for general case
            self.totalMipsCode.append(["exit:"])
            self.totalMipsCode.append(["li $v0,10"])
            self.totalMipsCode.append(["syscall"])
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
        


    def handleBlock(self,start,end,currentBlock):
        lines = []

        originalLines = self.lines
        blockDeclaration = currentBlock + ":"

        for i in range(start,end+1):
            lines.append(originalLines[i])

        self.totalMipsCode.append([blockDeclaration])
        self.compile(True,lines)
        self.totalMipsCode.append(["jr $ra"])

        self.lines = originalLines






#this is not going to be changed from now on
#all we are gon go from now on is adding all the other 
#operation handlers and call them wherever they are needed

def main(inputFile,outputFile):
    compiler = Compiler(inputFile)
    res = compiler.syntaxCorrect()

    if res == True:
        try:
            code,data = compiler.compile()

        except:
            code = False
            data = "There was an error while compiling"

        if code == False:
            print(data)
            return
        
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

    else:
        print(res)


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
        self.editor.insert(tk.END, "// Here goes your c++ code...")
        self.output.insert(tk.END, "### Here goes the Mips Assembly\n")


    def create_widgets(self):
        # Text Editor with line numbers
        editor_frame = tk.Frame(self)
        editor_frame.pack(side='left', expand=True, fill='both')

        self.editor = tk.Text(editor_frame, width=80, height=25, bg='black', fg='white',
                              insertbackground='white', selectbackground='gray', selectforeground='white',
                              font=("Consolas", 12))
        self.editor.pack(side='left', expand=True, fill='both')
        self.editor.tag_configure("line", background="black", foreground='gray')
        self.editor.bind("<Key>", self.update_line_numbers)
        self.scrollbar = tk.Scrollbar(editor_frame, command=self.editor.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.editor.config(yscrollcommand=self.scrollbar.set)
        self.linenumbers = tk.Text(editor_frame, width=4, height=25, bg="black", fg="gray", font=("Consolas", 12))
        self.linenumbers.pack(side='left', fill='y')
        self.linenumbers.insert('end', '1\n', 'line')
        self.linenumbers.config(state='disabled')

        # Buttons
        button_frame = tk.Frame(self, bg='black')
        button_frame.pack(side='top', anchor='ne')

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_editor, bg='red', fg='white')
        self.clear_button.pack(side='right', padx=5, pady=5)

        self.run_button = tk.Button(button_frame, text="Run", command=self.run_compiler, bg='blue', fg='white')
        self.run_button.pack(side='right', padx=5, pady=5)

        # Output area
        self.output = tk.Text(self, width=80, height=20, bg='black', fg='white', insertbackground='white',
                              font=("Consolas", 12))
        self.output.pack(side='bottom', fill='x')

        # Set the remaining space to be black
        self.config(bg='black')

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
        main('input.txt','output.txt')

        #and finally we out put the mips code 
        with open('output.txt', 'r') as result:
            for line in result:
                self.output.insert(tk.END, line)

        

    def clear_editor(self):
        self.editor.delete(1.0, tk.END)
        self.output.delete(1.0, tk.END)
        self.linenumbers.config(state='normal')
        self.linenumbers.delete(1.0, tk.END)
        self.linenumbers.insert('end', '1\n', 'line')
        self.linenumbers.config(state='disabled')


root = tk.Tk()
root.configure(bg='black')
app = Application(master=root)
app.mainloop()

