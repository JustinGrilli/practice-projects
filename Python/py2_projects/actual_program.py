def split_by(string, splitBy):
    stringList = string.split(splitBy)
    return stringList

user_string = raw_input("Type a series words: ")
user_split_by = raw_input("Now tell me what is between each of your words: ")
user_list = split_by(user_string, user_split_by)
print "\nGreat! Here are your words, in the order you gave them to me...\n"

item_order = 0
for item in user_list:
    print str(item_order) + '. ' + item
    item_order += 1

user_choice = input("Choose a number from your list: ")

print "Great you chose: " + user_list[user_choice]

raw_input('\n...Press Enter...')