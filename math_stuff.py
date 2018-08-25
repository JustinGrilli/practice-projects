def max_num(list):
    biggest_num = list[0]
    for item in list:
        if item > biggest_num:
            biggest_num = item
    return biggest_num


my_nums = [2,7,8,9,15,1,17,200,9000,9001,0]

print max_num(my_nums)

