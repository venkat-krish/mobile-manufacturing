##################################################################################################
# Assignment 2: Problem PS1
# Group #: AS2_CH1_B1_G6
# Members: Venkataramanan K, Bala Kavin Pon, Balavijay D
# Problem Statement: 
#   Mobile manufacturing tasks should be scheduled in an optimized manner such that the idle time of 
#   assembly unit should be in minimal time.
##################################################################################################

import logging
import os

# Instantiation of logger object
logger = logging.getLogger(__name__)

"""
    Task class is a data structure for the mobile manufacture tasks.
    Attributes:
        Task Id
        Manufacture time
        Assemble Time
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
        task_task_list = []
        try:
            with open(input_file, 'r+') as tfp:
                task_task_list =  [self.__map_task(line) for line in tfp.readlines()]
                tfp.close() # Close the file handler
        except ValueError as ve:
            logger.error("Invalid input data please correct your input and re-run the program.\t<{0}>".format(ve))
        except FileNotFoundError as fne:
            raise FileNotFoundError(fne)
        
        return task_task_list

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
    def merge_sort_tasks(self, task_list):
        if len(task_list) > 1: # Return condition: Checking the size of the task_list should be more than 1
            mid = len(task_list)//2
            left = task_list[:mid]
            right = task_list[mid:]
            # Recursive call with left and right split of task_list
            self.merge_sort_tasks(left)
            self.merge_sort_tasks(right)
            
            i=j=k=0
            
            while i < len(left) and j < len(right):
                # whenever left element manufacture time is lesser than the right element manufacture time then 
                # add the left item first
                if left[i].manufacture_time < right[j].manufacture_time: 
                    task_list[k] = left[i]
                    i+=1
                elif left[i].manufacture_time == right[j].manufacture_time: # When the left & right elements manufacture time are same then go for assemble time
                    if left[i].assemble_time < right[j].assemble_time: # if right assemble time is larger than the left then move the right element.
                        task_list[k] = right[j]
                        j+=1
                    else:
                        task_list[k] = left[i]
                        i+=1
                else: # When right elements manufacture time is larger
                    task_list[k] = right[j]
                    j+=1
                k+=1

            # Left iteration happens only when the index is still lesser than the length of left split.
            while i < len(left):
                task_list[k] = left[i]
                i += 1
                k += 1
            # right iteration happens only when the index is still lesser than the length of right split.
            while j < len(right):
                task_list[k] = right[j]
                j += 1
                k += 1
    
    
    """"
        schedule() - Schedule function does the scheduling activity of the tasks given 
    """
    def schedule(self):
        # 1. Copy of the input task list
        task_list = self.tasks[:]
        # 2. Invoking merge sort function to sort the tasks
        self.merge_sort_tasks(task_list)
        logger.debug("Sorted jobs {0}".format(task_list))
        # 3. Invocation of runtime assembly unit idle time
        self.write_result(self.__get_runtime_assembly_idle(task_list))

    """
        Extract Total run time and wait time in units 
    """
    def __get_runtime_assembly_idle(self,task_list):
        run_time = assemble_time = idle_time = lag = 0
        job_sequence = list()
        
        for i in range(0, len(task_list)):
            # Add the optimal jobs in the sequence of running.
            job_sequence.append(task_list[i].task_id)
            # Running time indicates the sum of parts manufacture time.
            run_time += task_list[i].manufacture_time  # manufacturing unit runs in sequence also its current scale for run time
            # Time difference is runtime - (idle time and assemble time)
            time_diff = run_time - (idle_time + assemble_time)  # compute the time_difference in assembly time of previous values
        
            if (time_diff > 0):                            #  +ve means add to idle time
                idle_time += time_diff                     #  -ve means its a task_list forward lag
                lag = 0
            else:
                lag = -time_diff
            # Take the sum of assembly time
            assemble_time += task_list[i].assemble_time

        # Overall production time includes runtime + lag time + last item's assemble time
        total_time = run_time + lag + task_list[len(task_list)-1].assemble_time
        logger.debug("Sequence list: {0}, Idle : {1}, Prod Time: {2}".format(job_sequence, idle_time, total_time))

        return (job_sequence, total_time, idle_time)

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