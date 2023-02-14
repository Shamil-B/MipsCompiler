class Compiler():
    def __init__(self) -> None:
        self.varCount = 0

    def syntaxCorrect(self):
        return True

    def compile(self):
        totalMipsCode = []
        totalMipsData = []
        lines = []

        # Open a file in read mode
        with open('cppToCompile.txt', 'r') as inputFile:
            # Iterate over each line in the inputFile
            for line in inputFile:
                # Process the line (e.g. print it)
                lines.append(line.strip())

        lines.pop(0)
        lines.pop(0)

        #now we can do anything we want
        for line in lines:
            if line.startswith("cout"):
                code,data = self.handlePrint(line)
                totalMipsCode.append(code)
                totalMipsData.append(data)
            
        return totalMipsCode,totalMipsData

    def handlePrint(self,line):
        printableWord = line[8:-1]
        variablName = "var"+str(self.varCount)
        mipsCode = ["li $v0,4","la $a0 "+variablName,"syscall"]
        mipsData = [variablName+f': .asciiz "{printableWord}"']
        self.varCount += 1

        return mipsCode,mipsData




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
