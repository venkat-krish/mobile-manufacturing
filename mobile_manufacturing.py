import logging
import os

logger = logging.getLogger(__name__)

"""
    Task class is a data structure for the mobile manufacture tasks.
"""
class Task():

    def __init__(self, task_id, manufacture_time, assemble_time):
        self.task_id = task_id
        self.manufacture_time = manufacture_time
        self.assemble_time = assemble_time
    
    def __repr__(self):
        return "Task object: {0}, {1}, {2}".format(self.task_id, self.manufacture_time, self.assemble_time)

"""
    ManufactureMobile collects the tasks from the input file and finds the sequence of mobile manufacturing using 
    task scheduling algorithm.
"""
class ManufactureMobile():

    RESULT_MSGS = ['Mobiles should be produced in the order: {0}',
    'Total production time for all mobiles is: {0}',
    'Idle Time of Assembly unit: {0}']

    def __init__(self, input_file, output_file):
        try:
            self.tasks = self.__fetch_tasks(input_file)
            
            self.output_file=output_file # Output file to write the result of job scheduling.
        except FileNotFoundError as fne:
            logger.error("Input file is not found. Please provide valid input file.\t<{0}>".format(fne))

    def __fetch_tasks(self, input_file):
        task_arr = []
        try:
            with open(input_file, 'r+') as tfp:
                task_arr =  [self.__map_task(line) for line in tfp.readlines()]
                tfp.close() # Close the file handler
        except ValueError as ve:
            logger.error("Invalid input data please correct your input and re-run the program.\t<{0}>".format(ve))
        except FileNotFoundError as fne:
            raise FileNotFoundError(fne)
        
        return task_arr

    def __map_task(self, task_info):
        try:
            task_parts = [ int(val) for val in task_info.strip().split('/')]
           
            return Task(task_parts[0], task_parts[1], task_parts[2])
        except ValueError as ve:
            raise ValueError(ve)

    """
        merge_sort_tasks()-function sorts the task list based on the manufacture and assemble time
        it uses the merge sort algorithm. 
        the complexity of the runtime for this function is O(nlogn).
    """
    def merge_sort_tasks(self, arr):
        if len(arr) > 1: # Return condition: Checking the size of the array should be more than 1
            mid = len(arr)//2
            left = arr[:mid]
            right = arr[mid:]
            # Recursive call with left and right split of array
            self.merge_sort_tasks(left)
            self.merge_sort_tasks(right)
            
            i=j=k=0
            
            while i < len(left) and j < len(right):
                # whenever left element manufacture time is lesser than the right element manufacture time then 
                # add the left item first
                if left[i].manufacture_time < right[j].manufacture_time: 
                    arr[k] = left[i]
                    i+=1
                elif left[i].manufacture_time == right[j].manufacture_time: # When the left & right elements manufacture time are same then go for assemble time
                    if left[i].assemble_time < right[j].assemble_time: # if right assemble time is larger than the left then move the right element.
                        arr[k] = right[j]
                        j+=1
                    else:
                        arr[k] = left[i]
                        i+=1
                else: # When right elements manufacture time is larger
                    arr[k] = right[j]
                    j+=1
                k+=1

            # Left iteration happens only when the index is still lesser than the length of left split.
            while i < len(left):
                arr[k] = left[i]
                i += 1
                k += 1
            # right iteration happens only when the index is still lesser than the length of right split.
            while j < len(right):
                arr[k] = right[j]
                j += 1
                k += 1
    
    
    """
        Schedule function does the scheduling activity of the tasks given 
    """
    def schedule(self):
        # 1. sort the tasks in based on the total production time in increasing order
        task_list = self.tasks[:]
        # Invoking merge sort function to sort the tasks
        self.merge_sort_tasks(task_list)        
        logger.debug("Sorted jobs {0}".format(task_list))
        
        job_sequence = list()
        idle_time = 0
        total_assemble_time = assemble_time = manufacture_time = 0
        production_time = 0

        # Iterate through the sorted task
        for i in range(0, len(self.tasks)):
            # Add the task to job sequence list
            job_sequence.append(task_list[i].task_id)           
           
            manufacture_time += task_list[i].manufacture_time
            # Assigning the current task assemble time for calculating the idle time.
            assemble_time += task_list[i].assemble_time

            # When the first item is at manufacture unit, take the time into Idle time
            if total_assemble_time == 0:
                idle_time = task_list[i].manufacture_time
            elif assemble_time < manufacture_time: # If the assemble time is more than manufacture time 
                # The difference will give an idle time of assembly unit
                idle_time += int(manufacture_time - assemble_time)
            # Collect the assemble time values in the a total assemble time
            total_assemble_time = assemble_time 
            logger.debug("Idle time {0}, {1}".format(idle_time, total_assemble_time))
                              
        # Sum of tasks assemble time and idle time gives total production time.
        production_time = total_assemble_time + idle_time

        logger.debug("Sequence list: {0}, Idle : {1}, Prod Time: {2}".format(job_sequence, idle_time, production_time))
        # Printing the result in a text file
        resultset = (job_sequence,  production_time, idle_time)
        # Invocation of write to file method
        self.write_result(resultset)

    """
        write_result() - it converts the output into resultant messages.
    """
    def write_result(self, resultset):
        try:
            self.__clear_output() # Flush out the old result in the output file
            # Constructing the result with proper message   
            output_msg = [ msg.format(val) for msg,val in zip(self.RESULT_MSGS, resultset)]

            self.__output_result(output_msg)
            logger.debug("Output message {0}".format(output_msg))
        except IOError as ie:
            logger.error("Unable to write the output result <{0}>".format(ie))


    """
        output_result() : It writes the output result into the output file.
        @param : Result message
    """
    def __output_result(self, result_msg):
        try:
            with open(self.output_file, 'a+') as ofp:
                for line in result_msg:
                    ofp.write("%s \n" % line) # Write the given result message into an output file.

        except IOError as ie:
            logger.error("Error in writing the result into output file")
    
    """
        clear_output(): Erase the content of the text file
    """
    def __clear_output(self):
        if os.path.exists(self.output_file) & os.path.isfile(self.output_file):
            with open(self.output_file, 'r+') as ofp:
                ofp.truncate(0)
        

if __name__ == '__main__':
    # Setting the log level as debug will make the program to print the debug statements
    logging.basicConfig(level=logging.INFO)

    # Input file name
    input_file = "./input/InputPS1.txt"
    output_file = "./output/OutputPS1.txt"

    try:
        # Instantiating the manufacturing class
        mobile_manufacture = ManufactureMobile(input_file, output_file)
        # Invoking the schedule method to find the optimized schedule of tasks
        mobile_manufacture.schedule()

        # Final message on the program completion
        logger.info("\n"+"==="*25+"\nProgram has successfully completed the execution.\nPlease check the /output/OutputPS1.txt file.\n"+"==="*25)
    except Exception as ex:
        logger.error("Exception occured in the program.<{0}>".format(ex))