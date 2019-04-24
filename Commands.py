from Main.models import Account, Course, Section, AccountSection, AccountCourse
import CurrentUserHelper
import re
from itertools import chain


class Command():

    def __init__(self, opcode, arguments, function):
        self.opcode = opcode
        self.arguments = arguments
        self.function = function


def login(userName, password):

    try:
        CurrentUser = Account.objects.get(userName=userName)
        if CurrentUser.password != password:
            raise Exception("Incorrect password")
        CurrentUser.currentUser = True
    except Account.DoesNotExist:
        raise Exception("Account Not Found")

    return CurrentUser


def logout(user):
    try:
        #CurrentUser = Account.objects.get(userName=userName)
        #CurrentUser.currentUser = False
        #CurrentUser.save()
        user.currentUser = False
        user.save()
        return "Successfully logged out"
    except Account.DoesNotExist:
        return "Please log in First"
    except Account.MultipleObjectsReturned:
        return "Multiple account Logged in, Something went terribly wrong"


def checkValidEmail(email):
    str = email.split('@', 1)
    if len(str) == 1 or str[1] != "uwm.edu":
        return False
    return True


def containsOnlyDigits(argument):
    if not re.match('^[0-9]*$', argument):
        return False
    return True


def checkVaildTimes(time):
    if len(time) != 4:
        return False
    if not re.match('^[0-2]*$', time[0]):
        return False
    for i in range(1, 3):
        if not (re.match('^[0-9]*$', time[i])):
            return False
    return True


def checkValidDays(days):
    daysnospaces = days.replace(" ", "")
    for i in daysnospaces:
        if i not in 'MTWRFN':
            return False
    return True


# Creating an Account
def createAccount(firstName, lastName, userName, title, email):

    # Check that the account trying to be created does not already exist
    if Account.objects.filter(userName=userName).exists():
        return "Account already exists"

    # Make sure the account is trying to be created with a UWM email address
    if checkValidEmail(email) == False:
        return "The email address you have entered in not valid.  " \
               "Please make sure you are using a uwm email address in the correct format."

    # If we get here the account is safe to be created.
    else:
        A = Account()
        A.userName = userName
        A.email = email
        if title.lower() == "ta":
            A.title = 1
        elif title.lower() == "instructor":
            A.title = 2
        else:
            return "Invalid title, account not created"
        A.firstName = firstName
        A.lastName = lastName
        # Make a temporary password for the newly created user
        A.password = A.userName + "456"
        A.save()

        return "Account successfully created.  Temporary password is: " + A.userName + "456"


def deleteAccountCom(userName):

    try:
        a = Account.objects.get(userName=userName)
    except Exception as e:
        return "Account does not exist"
    a.delete()
    return "Account successfully deleted"


def createCourse(name, number, online, days, start, end):
    # Check that the command has the appropriate number of arguments

    # Course number checks
    if not re.match('^[0-9]*$', number):
        return "Course number must be numeric and three digits long"
    if len(number) != 3:
        return "Course number must be numeric and three digits long"
    # Check that the course does not already exist
    if Course.objects.filter(number=number).exists():
        return "Course already exists"
    # Location checks
    if online.lower() != "online" and online.lower() != "campus":
        return "Location is invalid, please enter campus or online."
    # Days check
    for i in days:
        if i not in 'MTWRFN':
            return "Invalid days of the week, please enter days in the format: MWTRF or NN for online"
    # Check times
    startTime = start
    endTime = end
    if len(startTime) != 4 or len(endTime) != 4:
        return "Invalid start or end time, please use a 4 digit military time representation"
    if not re.match('^[0-2]*$', startTime[0]) or not re.match('^[0-1]*$', endTime[0]):
        return "Invalid start or end time, please use a 4 digit military time representation"
    for i in range(1, 3):
        if not (re.match('^[0-9]*$', startTime[i])) or not (re.match('^[0-9]*$', endTime[i])):
            return "Invalid start or end time, please use a 4 digit military time representation"

    # Else the course is ok to be created
    else:
        c = Course()
        c.name = name
        c.number = number
        if online.lower() == "online":
            c.onCampus = False
        else:
            c.onCampus = True
            c.classDays = days
            c.classHoursStart = start
            c.classHoursEnd = end
        c.save()
        return "Course successfully created"


def createSection(courseNumber, type, sectionNumber, days, start, end):
    # Course number checks
    if not re.match('^[0-9]*$', courseNumber):
        return "Course number must be numeric and three digits long"
    if len(courseNumber) > 3 or len(courseNumber) < 3:
        return "Course number must be numeric and three digits long"

    # Make sure course that the lab is being created for exists ok
    try:
        c = Course.objects.get(number=courseNumber)
    except Course.DoesNotExist:
        return "The Course you are trying to create a lab for does not exist"

    # Make sure the course is not online
    if c.onCampus == False:
        return "You cannot create a lab for an online course"

    # Section number checks
    if not re.match('^[0-9]*$', sectionNumber):
        return "Section number must be numeric and three digits long"
    if len(sectionNumber) > 3 or len(sectionNumber) < 3:
        return "Section number must be numeric and three digits long"

    # Days check
    for i in days:
        if i not in 'MTWRFN':
            return "Invalid days of the week, please enter days in the format: MWTRF"

    # Time checks
    if len(start) != 4 or len(end) != 4:
        return "Invalid start or end time, please use a 4 digit military time representation"
    if not re.match('^[0-2]*$', start[0]) or not re.match('^[0-2]*$', end[0]):
        return "Invalid start or end time, please use a 4 digit military time representation"
    for i in range(1, 3):
        if not (re.match('^[0-9]*$', start[i])) or not (re.match('^[0-9]*$', end[i])):
            return "Invalid start or end time, please use a 4 digit military time representation"

    # Make sure the lab does not already exist
    if Section.objects.filter(course=c, number=sectionNumber).exists():
        return "Lab already exists, lab not added"
    else:
        l = Section.objects.create(course=c)
        l.type = type
        l.sectionNumber = sectionNumber
        l.meetingDays = days
        l.startTime = start
        l.endTime = end
        l.save()
        return "Lab successfully created"


def assignAccCourse(userName, courseName):
    # Check if the course is valid
    if not Course.objects.filter(name=courseName).exists():
        return "Invalid course number"
    # Check if the user name is valid
    if not Account.objects.filter(userName=userName).exists():
        return "Invalid user name"

    instructor = Account.objects.get(userName=userName)
    course = Course.objects.get(number=Course.objects.get(name=courseName).number)
    # title represented as an integer where 4=supervisor 3=administrator
    # 2=Instructor 1=TA. 0=No current User
    # Check if the account is an instructor
    # Check if the course is already assigned
    # Otherwise(if there are no errors found), an instructor can be assigned to a course
    a = AccountCourse()
    a.Account = instructor
    a.Course = course
    a.save()
    return "Instructor was successfully assigned to class"


def assignAccSection(userName, courseNumber, sectionNumber):
    if not Account.objects.filter(userName=userName).exists():
        return "Invalid account name"

    if not Course.objects.filter(number=courseNumber).exists():
        return "Invalid course number"

    course = Course.objects.get(number=courseNumber)

    if not Section.objects.filter(number=sectionNumber, course=course).exists():
        return "Invalid lab section"

    ta = Account.objects.get(userName=userName)

    if not AccountCourse.objects.filter(Account=ta, Course=Course.objects.get(number=courseNumber)).exists():
        return "TA must be assigned to the Course first"

    lab = Section.objects.get(number=sectionNumber, course=course)

    if AccountSection.objects.filter(Section=lab).exists():
        return "Lab section already assigned"

    p = AccountSection()
    p.Account = ta
    p.Section = lab
    p.save()

    return "TA successfully assigned"


def displayAllCourseAssign():
    lst = Course.objects.all()
    courseList = []

    for a in lst:
        courseList.append(displayCourseAssign(a.number))

    return courseList


def displayCourseAssign(courseNumber):
    course = Course.objects.get(number=courseNumber)

    response = course.name + " CS" + str(course.number) + "\n"

    lst = AccountCourse.objects.filter(Course=course)
    instructorList = []

    for a in lst:
        if a.Account.title == 2:
            instructorList.append(str(a.Account))

    response += "Instructors: "
    if not instructorList:
        response += "None"
    else:
        response += ", ".join(instructorList)
        #for a in instructorList:
            #response += a + " "

    response += "\nTeaching Assistants: "

    taList = []

    for a in lst:
        if a.Account.title == 1:
            taList.append(str(a.Account))

    if not taList:
        response += "None"
    else:
        response += ", ".join(taList)
        #for a in taList:
            #response += a + " "
    response += "\n"
    lecSectionList = Section.objects.filter(course=course, type=1)
    labSectionList = Section.objects.filter(course=course, type=0)
    if not lecSectionList and not labSectionList:
        response += "No sections found"
        return response
    else:
        for a in lecSectionList:
            p = AccountSection.objects.filter(Section=a)
            if not p:
                response += str(a) + ": None\n"
            else:
                for q in p:
                    response += str(q.Section) + ": " + str(q.Account) + "\n"
        for a in labSectionList:
            p = AccountSection.objects.filter(Section=a)
            if not p:
                response += str(a) + ": None\n"
            else:
                for q in p:
                    response += str(q.Section) + ": " + str(q.Account) + "\n"

    return response


def viewCourseAssign(userName): # secret message
    if not Account.objects.filter(userName=userName).exists():
        return "Account not found"

    account = Account.objects.get(userName=userName)

    if not AccountCourse.objects.filter(Account=account).exists():
        return str(account) + " does not have any assignments"

    labAssignments = AccountSection.objects.filter(Account=account)

    response = str(account) + " is assigned to: "
    labList = []
    checkList = []
    for a in labAssignments:
        labList.append(str(a.Section))
        checkList.append(a.Section.course)

    response += ", ".join(labList)

    courseAssignments = AccountCourse.objects.filter(Account=account)

    courseList = []
    first = True
    for a in courseAssignments:
        if a.Course not in checkList:
            if first and len(labAssignments) != 0:# all this does is puts a comma after lab sections if present
                response += ", "
                first = False
            courseList.append(str(a.Course))

    response += ", ".join(courseList)

    return response


def getPublicDataList():
    instructorList = Account.objects.filter(title=2)
    taList = Account.objects.filter(title=1)
    # staffList = list(chain(instructorList, taList))
    staffList = instructorList | taList
    directory = []

    for i in staffList:
        directory.append(i.displayPublic())

    directory.sort()
    return directory


def getPrivateDataList():
    instructorList = Account.objects.filter(title=2)
    taList = Account.objects.filter(title='1')
    # staffList = list(chain(instructorList, taList))
    staffList = instructorList | taList
    directory = []

    for i in staffList:
        directory.append(i.displayPrivate())

    directory.sort()
    return directory


def editPubInfo(user, dict):

    firstName = dict['firstName']
    if firstName != user.firstName:
        if not firstName.replace(" ", "").isalpha():
            return "First Name can only contain letters"
        user.firstName = firstName


    lastName = dict['lastName']
    if lastName != user.lastName:
        if not lastName.replace(" ", "").isalpha():
            return "Last name can only contain letters"
        user.lastName = lastName


    # Email
    email = dict['email']
    if email != user.email:
        if checkValidEmail(email) == False:
            return "The email address you have entered in not valid.  " \
                "Please make sure you are using a uwm email address in the correct format."
        else:
            user.email = email

    # Password
    password = dict['password']
    if password != user.password:
        user.password = password

    # Home phone
    homePhone = dict['homephone']
    if homePhone != str(user.homePhone):
        if containsOnlyDigits(homePhone.replace("-", "")) == False:
            return "Home Phone can only contain numbers"
        else:
            user.homePhone = homePhone

    # Address
    address = dict['address']
    if address != user.address:
        user.address = address

    # City
    city = dict['city']
    if city != user.city:
        if not city.replace(" ", "").isalpha():
            return "City must contain only letters"
        user.city = city

    # State
    state = dict['state']
    if state != user.state:
        if not state.replace(" ", "").isalpha():
            return "State must contain only letters"
        user.state = state

    # Zip Code
    zipCode = dict['zipcode']
    if zipCode != str(user.zipCode):
        if containsOnlyDigits(zipCode) == False:
            return "ZipCode my be only numeric"
        else:
            user.zipCode = zipCode

    # Office Number
    officeNumber = dict['officenumber']
    if officeNumber != str(user.officeNumber):
        if containsOnlyDigits(officeNumber) == False:
            return "Office Number must be numeric"
        else:
            user.officeNumber = officeNumber

    # Office phone
    officePhone = dict['officephone']
    if officePhone != str(user.officePhone):
        if containsOnlyDigits(officePhone.replace("-", "")) == False:
            return "Office Phone can only contain numbers"
        else:
            user.officePhone = officePhone

    # Office days
    officeDays = dict['officedays']
    if officeDays != user.officeDays:
        if checkValidDays(officeDays) == False:
            return "Invalid days of the week, please enter days in the format: MWTRF or NN for online"
        else:
            user.officeDays = officeDays

    # Start Time and End Time
    officeHoursStart = dict['officestart']
    officeHoursEnd = dict['officeend']
    if (officeHoursStart != str(user.officeHoursStart)):
        if checkVaildTimes(officeHoursStart) == False:
            return "Invalid start or end time, please use a 4 digit military time representation"
        else:
            user.officeHoursStart = officeHoursStart
    if officeHoursEnd != str(user.officeHoursEnd):
        if checkVaildTimes(officeHoursEnd) == False:
            return "Invalid start or end time, please use a 4 digit military time representation"
        else:
            user.officeHoursEnd = officeHoursEnd


    # Save changes
    user.save()

    return "Fields successfully updated"


def getCommands():
    return [Command("login", 2, login), Command("logout", 0, logout),
            Command("createaccount", 5, createAccount), Command("deleteaccount", 1, deleteAccountCom),
            Command("createcourse", 6, createCourse), Command("createsection", 6, createSection),
            Command("assignacccourse", 2, assignAccCourse),
            Command("assignaccsection", 3, assignAccSection),
            Command("viewcourseassign", 1, viewCourseAssign)]

