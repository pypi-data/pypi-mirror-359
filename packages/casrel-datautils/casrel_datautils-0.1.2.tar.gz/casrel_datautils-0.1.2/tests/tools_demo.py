
from casrel_datautils.Base_Conf import BaseConfig
from casrel_datautils.data_loader import get_data
baseconf = BaseConfig(bert_path="bert-base-chinese",
                      train_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\test.json",
                      test_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\one_Sample.json",
                      rel_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\relation.json", max_length=128)
dataloaders = get_data(baseconf)
print(dataloaders)
print(dataloaders.items())
for batch in dataloaders["dev_dataloader"]:
    print( batch)