from basetrainer import BaseTrainer
from losses import DetectorLoss
from coco_dataset import CocoDataset
from synthetic_dataset import SyntheticDataset


class MagicPointTrainer(BaseTrainer):
    def __init__(self, dataset_path, checkpoint_path, settings, use_coco=False):
        if use_coco:
            self.train_dataset = CocoDataset(dataset_path, settings, 'train', do_augmentation=False)
            self.test_dataset = CocoDataset(dataset_path, settings, 'test', do_augmentation=False, size=1000)
        else:
            self.train_dataset = SyntheticDataset(dataset_path, settings, 'training')
            self.test_dataset = SyntheticDataset(dataset_path, settings, 'test')
        super(MagicPointTrainer, self).__init__(settings, checkpoint_path, self.train_dataset, self.test_dataset)
        self.loss = DetectorLoss(self.settings.cuda)

    def train_loss_fn(self, image, true_points, *args):
        prob_map, descriptors, point_logits = self.model.forward(image)
        # image shape [batch_dim, channels = 1, h, w]
        if self.settings.cuda:
            true_points = true_points.cuda()
        loss_value = self.loss(point_logits, true_points, None)
        self.last_prob_map = prob_map
        self.last_labels = true_points
        self.last_image = image
        return loss_value

    def test_loss_fn(self, image, point_labels, *args):
        points_prob_map, descriptors, point_logits = self.model(image)
        if self.settings.cuda:
            point_labels = point_labels.cuda()
        loss_value = self.loss(point_logits, point_labels, None)
        return loss_value, point_logits

