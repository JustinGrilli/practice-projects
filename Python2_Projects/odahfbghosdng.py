this_list = ['a', 'b ', 'c\nd', '']

recon = []
for item in this_list:
    recon.append(item)
    count = len(' '.join(recon))
    print count