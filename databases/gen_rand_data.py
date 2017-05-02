import names, random
from random import randint

def gen_rand_data(id):
    """
    Generate Random data.
    """
    genders = ('male', 'female')
    gender = genders[randint(0,1)]
    fn = names.get_first_name(gender=gender)
    ln = names.get_last_name()
    full_name = fn + ' ' + ln
    # bas_ctr, \
    # str_ctr, car_ctr, swi_ctr, squ_ctr, total_ctr, rating, rating_ctr, login_time) \
    bas_ctr = randint(0,25)
    str_ctr = randint(0,25)
    car_ctr = randint(0,25)
    swi_ctr = randint(0,25)
    squ_ctr = randint(0,25)
    total_ctr = bas_ctr + str_ctr + car_ctr + swi_ctr + squ_ctr
    rating = 
    rating_ctr = 
    
    login_time = 



if __name__ == '__main__':
    