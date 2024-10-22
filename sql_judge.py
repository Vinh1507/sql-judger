import multiprocessing
import subprocess
import os
import time
import tasks

testcase1 = {
    'input_judge_sql': """
    CREATE TABLE test_table (
        id INT,
        name VARCHAR(50)
    );
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob');
    """,
}
testcase2 = {
    'input_judge_sql': """
    CREATE TABLE test_table (
        id INT,
        name VARCHAR(50)
    );
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob \n Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    """,
}

issue = {
    'user_sql': """
    SELECT * FROM test_table;
    """,
    'time_limit': 0.4,
    'memory_limit': 180,
    'testcases': [testcase1, testcase2],
}

if __name__ == "__main__":
    time_limit = issue['time_limit'] 

    processes = []
    result_queue = multiprocessing.Queue()

    count = 1
    for testcase in issue['testcases']:
        testcase['db_name'] = 'vinhbh' + str(count)
        count += 1
        p = multiprocessing.Process(target=tasks.judge_one_testcase, args=(result_queue, issue, testcase))
        processes.append(p)
        p.start()

    p.join()
    
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    print(results)

    # for p in processes:
    #     if p.is_alive():
    #         print(f"Dừng {p.name}...")
    #         p.terminate()  # Dừng process
    #         p.join()  # Đợi cho process kết thúc
    #     print(p)

    print("All processes have completed or been stopped.")
