import csv 


class Unpacker():

    @staticmethod
    def unpack_inputs():
        with open('inputs.csv') as i:
            csv_reader = csv.reader(i, delimiter=',')
            line_count = 0
            for line in csv_reader:
                print(line)
                line_count = line_count + 1
                if line_count == 10:
                    break
    
    
if __name__ == '__main__':
    Unpacker.unpack_inputs()