justin = "hey there %s, hows your %s?"

varb = ('betty', 'foot')
varc = ('tim', 'toe')
print justin % varc

example = "Hey now bessie nice chops"

print example.find('bessie')

sequence = ['hey', 'there', 'bessie', 'hoss']

glue = ' '
print glue.join(sequence)

randString = 'I wish I had A sausage'

print randString.upper()

truth = 'I love old women'

print truth.replace('old', 'hot')

book = {
    'Dad': 'Joe',
    'Mom': 'Sue',
    'Bro': 'Joey'
}
ages = {
    'Dad': 55,
    'Mom': 50,
    'Bro': 28
}
ages_backup = ages.copy()
print book['Bro']
print ages['Bro']
book.clear()
print book

print ages_backup.has_key('Mom')