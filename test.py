import time
from collections import Counter


def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        return result
    return wrapper

@log_execution_time
def count_words_dict(text):
    word_counts = {}
    for word in text.split():
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

@log_execution_time
def count_words_counter(text):
    Counter(text.split())



with open('shakespeare.txt', 'r') as f:
    text = f.read()
    
dict_execution_times = []
counter_execution_times = []
for i in range(100):
    start_time_dict = time.time()
    word_count_dict = count_words_dict(text)
    end_time_dict = time.time()
    word_count_counter = count_words_counter(text)
    end_time_counter = time.time()
    dict_execution_times.append(end_time_dict - start_time_dict)
    counter_execution_times.append(end_time_counter - end_time_dict)


# Calculate the mean and variance of the execution times
dict_mean_time = sum(dict_execution_times) / len(dict_execution_times)
dict_variance = sum((x - dict_mean_time) ** 2 for x in dict_execution_times) / len(dict_execution_times)

counter_mean_time = sum(counter_execution_times) / len(counter_execution_times)
counter_variance = sum((x - counter_mean_time) ** 2 for x in counter_execution_times) / len(counter_execution_times)