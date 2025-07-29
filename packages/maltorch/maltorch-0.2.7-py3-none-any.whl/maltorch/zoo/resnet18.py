from torchvision.models import resnet18
from maltorch.zoo.model import GrayscaleModel


class ResNet18(GrayscaleModel):
    def __init__(self, threshold: float = 0.5):
        super(ResNet18, self).__init__(
            name="ResNet18", gdrive_id="1N1uK8bsfJvB88ryZcbRfxkzerblXqMqg"
        )
        self.model = resnet18(num_classes=1)
        self.threshold = threshold

    def forward(self, x):
        y = self.model(x)
        return y
