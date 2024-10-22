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
    """
}
testcase2 = {
    'input_judge_sql': """
        CREATE TABLE test_table (
            id INT,
            name VARCHAR(50)
        );
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
        INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob'), (3, 'asdf'), (4, 'asdfasdfasdfasdf');
    """
}

issue = {
    'user_sql': """
        SELECT * FROM test_table;
    """,
    'time_limit': 0.5,
    'memory_limit': 90,
    'testcases': [testcase1, testcase2],
}

if __name__ == "__main__":
    time_limit = issue['time_limit'] 

    processes = []

    # Generate database names

    # Tạo và khởi động các tiến trình
    count = 1
    for testcase in issue['testcases']:
        testcase['db_name'] = 'vinhbh' + str(count)
        count += 1
        # tasks.judge_one_testcase(issue, testcase)
        p = multiprocessing.Process(target=tasks.judge_one_testcase, args=(issue, testcase))
        processes.append(p)
        p.start()

    time.sleep(time_limit)
    
    for p in processes:
        if p.is_alive():
            print(f"Dừng {p.name}...")
            p.terminate()  # Dừng process
            p.join()  # Đợi cho process kết thúc

    print("Tất cả các tiến trình đã hoàn thành hoặc bị dừng.")
