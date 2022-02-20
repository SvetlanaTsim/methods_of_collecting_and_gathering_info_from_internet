from task_2_1_main_function import get_all_vacancies_data

text = 'Python'
df = get_all_vacancies_data(text)

print(df.info)
df.to_csv('hh_superjob_vacancies_python_parsing.csv', index=False)
