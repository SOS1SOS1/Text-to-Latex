import pytorch_lightning as pl
import torch
import cv2
from torchvision.models import resnet18
from torch import nn
import numpy as np

classes_mapping = []
three_letter_func = set(['\\log', '\\cos', '\\sin', '\\tan', '\\lim'])

with open('classes.txt', 'r') as f:
  classes_mapping = f.readlines()
  for i in range(len(classes_mapping)):
    classes_mapping[i] = classes_mapping[i].rstrip()

class ResNetCROHME(pl.LightningModule):
  def __init__(self, num_classes=101):
    super().__init__()
    self.model = resnet18(num_classes=num_classes)
    self.model.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
    self.loss = nn.CrossEntropyLoss()

  def forward(self, x):
    return self.model(x)
  
  def training_step(self, batch, batch_no):
    x, y = batch
    logits = self(x)
    loss = self.loss(logits, y)
    return loss
  
  def configure_optimizers(self):
    return torch.optim.RMSprop(self.parameters(), lr=0.005)

def get_char_prediction(img_data, checkpoint_file='resnet18_crohme_char.pt', return_str=True):
  img_data = cv2.resize(img_data, (50, 50)) / 255
  img_data = np.reshape(img_data, (1,1,50,50))
  inference_model = ResNetCROHME.load_from_checkpoint(checkpoint_file)
  inference_model.freeze() # prepares model for predicting
  probabilities = torch.softmax(inference_model(torch.FloatTensor(img_data)), dim=1)
  sorted_args = torch.argsort(probabilities, dim=1, descending=True)[0]
  args_idx = 0
  while classes_mapping[sorted_args[args_idx]] in three_letter_func:
    args_idx += 1
  predicted_class = sorted_args[args_idx]
  if return_str:
    predicted_class = classes_mapping[predicted_class]

  return predicted_class, probabilities