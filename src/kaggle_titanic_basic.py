__author__ = 'pavzi (Pavol Zilecky, pavol.zilecky@gmail.com)'

# The first thing to do is to import the relevant packages
# that I will need for my script,
# these include the Numpy (for maths and arrays)
# and csv for reading and writing csv files
# If i want to use something from this I need to call
# csv.[function] or np.[function] first

import csv as csv
import numpy as np

# Open up the csv file in to a Python object
train_file_object = csv.reader(open('csv/train.csv', 'rb'))
header = train_file_object.next()  # The next() command just skips the first line which is a header

data = []  # Create a variable called 'data'.
for row in train_file_object:  # Run through each row in the csv file, adding each row to the data variable
    data.append(row)

data = np.array(data)  # Then convert from a list to an array
# Be aware that each item is currently a string in this format

# The size() function counts how many elements are in
# in the array and sum() (as you would expects) sums up
# the elements in the array.

number_passengers = np.size(data[0::, 1].astype(np.float))
number_survived = np.sum(data[0::, 1].astype(np.float))
proportion_survivors = number_survived / number_passengers

print 'Number of passengers is %s' % number_passengers
print 'Number of people who survived is %s' % number_survived
print 'Proportion of people who survived is %s' % proportion_survivors

women_only_stats = data[0::, 4] == "female"  # This finds where all
# the elements in the gender
# column that equals female
men_only_stats = data[0::, 4] != "female"  # This finds where all the
# elements do not equal
# female (i.e. male)

# Using the index from above we select the females and males separately
women_onboard = data[women_only_stats, 1].astype(np.float)
men_onboard = data[men_only_stats, 1].astype(np.float)

# Then we finds the proportions of them that survived
proportion_women_survived = np.sum(women_onboard) / np.size(women_onboard)
proportion_men_survived = np.sum(men_onboard) / np.size(men_onboard)

# and then print it out
print 'Proportion of women who survived is %s' % proportion_women_survived
print 'Proportion of men who survived is %s' % proportion_men_survived

# ########################################################################
# Creating a gender based model
#########################################################################

test_file = open('csv/test.csv', 'rb')
test_file_object = csv.reader(test_file)
test_file_header = test_file_object.next()

prediction_file = open('genderbasedmodel.csv', 'wb')
prediction_file_object = csv.writer(prediction_file)

prediction_file_object.writerow(['PassengerId', 'Survived'])

for row in test_file_object:
    if row[3] == 'female':
        prediction_file_object.writerow([row[0], '1'])
    else:
        prediction_file_object.writerow([row[0], '0'])

test_file.close()
prediction_file.close()

#########################################################################
#                   Creating a survival table model
#########################################################################

print header
print data[0]
print data[1]

# So we add a ceiling
fare_ceiling = 40
# then modify the data in the Fare column to = 39, if it is greater or equal to the ceiling
data[data[0::, 9].astype(np.float) >= fare_ceiling, 9] = fare_ceiling - 1.0

fare_bracket_size = 10
number_of_price_brackets = fare_ceiling / fare_bracket_size

# I know there were 1st, 2nd and 3rd classes on board
number_of_classes = 3

# But it's better practice to calculate this from the data directly
# Take the length of an array of unique values in column index 2
number_of_classes = len(np.unique(data[0::, 2]))

# Initialize the survival table with all zeros
survival_table = np.zeros((2, number_of_classes, number_of_price_brackets))

for i in xrange(number_of_classes):  # loop through each class
    for j in xrange(number_of_price_brackets):  # loop through each price bin

        # Which element is a female/male and was i-th class
        # was greater than this bin and less than the next bin in the 2-nd col
        women_only_stats = data[(data[0::, 4] == "female") &
                                (data[0::, 2].astype(np.float) == i + 1) &
                                (data[0:, 9].astype(np.float) >= j * fare_bracket_size) &
                                (data[0:, 9].astype(np.float) < (j + 1) * fare_bracket_size), 1]
        men_only_stats = data[(data[0::, 4] != "female") &
                              (data[0::, 2].astype(np.float) == i + 1) &
                              (data[0:, 9].astype(np.float) >= j * fare_bracket_size) &
                              (data[0:, 9].astype(np.float) < (j + 1) * fare_bracket_size), 1]

        survival_table[0, i, j] = np.mean(women_only_stats.astype(np.float))
        survival_table[1, i, j] = np.mean(men_only_stats.astype(np.float))

# Replace nans to zero
survival_table[survival_table != survival_table] = 0

# If number of survived passengers for given category is more than half, we assume
# that all future passengers in these category survived
survival_table[survival_table < 0.5] = 0
survival_table[survival_table >= 0.5] = 1

test_file = open('csv/test.csv', 'rb')
test_file_object = csv.reader(test_file)
test_file_header = test_file_object.next()

prediction_file = open('genderclassfaremodel.csv', 'wb')
prediction_file_object = csv.writer(prediction_file)

prediction_file_object.writerow(['PassengerId', 'Survived'])

for row in test_file_object:

    # convert to number
    try:
        row[8] = float(row[8])
    except:
        row[8] = 3 - float(row[1])

    # check whether fare is not bigger then the highest allowed value
    if row[8] > fare_ceiling:
        row[8] = fare_ceiling - 1

    # Add bin fare number according to fare
    bin_fare = int(np.floor(row[8] / fare_bracket_size))

    if row[3] == 'female':
        prediction_file_object.writerow([row[0], int(survival_table[0, float(row[1]) - 1, bin_fare])])
    else:
        prediction_file_object.writerow([row[0], int(survival_table[1, float(row[1]) - 1, bin_fare])])


test_file.close()
prediction_file.close()