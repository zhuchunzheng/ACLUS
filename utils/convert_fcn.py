from torchvision.models.segmentation import FCN
from torchvision.models.resnet import resnet18, resnet50
import torch
# from detectron2.checkpoint import DetectionCheckpointer
import pickle
from torchvision.models._utils import IntermediateLayerGetter
import sys
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
src = '/home/zhuchunzheng/Projects/detcon/ckpt/detconb_US30Kgt_resnet18_all/07_24_16-39/07_24_16-39_resnet18_220.pth.tar'
tgt = '/home/zhuchunzheng/Projects/detcon/ckpt/detconb_US30Kgt_resnet18_all/07_24_16-39_resnet18_220.pth'
print(src,tgt)
#exit()
obj = torch.load(src)['model']
newmodel = {}
for k in list(obj.keys()):
        if "module.online_network.encoder." not in k: #Only use online network encoder param
            obj.pop(k)
            continue
        else:
            old_k = k
            k = k[len("module.online_network.encoder."):] #Remove byol model prefix
        if k[0] in ["0", "1"]:
            if k[0] == "0": #To match typical torchvision convention (our 0 -> conv1)
                k = "conv1" + k[1:]
            else: # bn1 param
                k = "bn1" + k[1:]
        for t in [1, 2, 3, 4]:
            k = k[0].replace("{}".format(t+3), "layer{}".format(t )) + k[1:]
        print(k)
        newmodel[k] = obj.pop(old_k).detach()

newmodel['fc.weight']=torch.rand(1000,512)
# newmodel['fc.weight']=torch.rand(1000,2048)
newmodel['fc.bias']=torch.rand(1000)
        
backbone = resnet18(pretrained=False)
# backbone = resnet50(pretrained=False, replace_stride_with_dilation=[False, True, True])
#
return_layers = {"layer4": "out"}
return_layers["layer3"] = "aux"
print(backbone)
#backbone = IntermediateLayerGetter(backbone,)
backbone.load_state_dict(newmodel)
torch.save(backbone.state_dict(),tgt)