def normalize_data(n_cases, n_people, scale):
    # TODO) Calculate the number of cases per its population
    norm_cases = []
    for idx, n in enumerate(n_cases):
        norm_cases.append((n/n_people[idx])*scale)
    return norm_cases

regions  = ['Seoul', 'Gyeongi', 'Busan', 'Gyeongnam', 'Incheon',
            'Gyeongbuk', 'Daegu', 'Chungnam', 'Jeonnam', 'Jeonbuk',
            'Chungbuk', 'Gangwon', 'Daejeon', 'Gwangju', 'Ulsan', 'Jeju',
            'Sejong']

n_people = [9550227, 13530519, 3359527, 3322373, 2938429, 2630254, 2393626, 2118183, 1838353,
            1792476, 1597179, 1536270, 1454679, 1441970, 1124459, 675883, 365309]  # 2021-08

n_covid  = [644, 529, 38, 29, 148, 28, 41, 62, 23, 27, 27, 33, 16, 40, 20, 5, 4]  # 2021-09-21

sum_people = sum(n_people)  # TODO) Compute the total number of people
sum_covid = sum(n_covid)   # TODO) Compute the total number of new cases
norm_covid = normalize_data(n_covid, n_people, 1000000)  # cases per 1 million people

# Print population by region
print('### Korean Population by Region')
print('* Total population:', sum_people)
print()
print('| Region | Population | Ratio (%) |')
print('| ------ | ---------- | --------- |')
for idx, pop in enumerate(n_people):
    ratio = (pop / sum_people) * 100
    print('| %s | %d | %.1f |' % (regions[idx], pop, ratio))

print('')  

print('### Korean COVID-19 New Cases by Region (2021-09-21)')
print('* Total new cases:', sum_covid)
print()
print('| Region | New Cases | Cases per 1M people |')
print('| ------ | --------- | ------------------- |')
for idx, cases in enumerate(n_covid):
    print('| %s | %d | %.1f |' % (regions[idx], cases, norm_covid[idx]))
