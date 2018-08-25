face = [21, 18, 30]

face.append(45)

print face

apples = ['i', 'love', 'apples', 'apples', 'now']

print apples.count('apples')
one = [1, 2, 3]
two = [4, 5, 6]

one.extend(two)
print one

print apples.index('love')

apples.insert(apples.index('love'), 'orange')
apples.pop(apples.index('love'))
apples.remove('apples')
apples.reverse()
print apples

numbers = [2, 5, 15, 0, -99, 23, 3]

print numbers

numbers.sort()
print numbers

print sorted('justango')

myname = 'Justango 69'

if 'something' in myname:
    print 'something'
elif 'anotherone' in myname:
    print 'anotherone'
else:
    print 'Draw'