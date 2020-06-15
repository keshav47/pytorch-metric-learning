import unittest
import torch
from pytorch_metric_learning.losses import GeneralizedLiftedStructureLoss
from pytorch_metric_learning.utils import common_functions as c_f

class TestGeneralizedLiftedStructureLoss(unittest.TestCase):
    def test_generalized_lifted_structure_loss(self):
        neg_margin = 0.5
        loss_func = GeneralizedLiftedStructureLoss(neg_margin=neg_margin)

        embedding_angles = [0, 20, 40, 60, 80]
        embeddings = torch.tensor([c_f.angle_to_coord(a) for a in embedding_angles], requires_grad=True, dtype=torch.float) #2D embeddings
        labels = torch.LongTensor([0, 0, 1, 1, 2])

        loss = loss_func(embeddings, labels)
        loss.backward()

        pos_pairs = [(0,1), (1,0), (2,3), (3,2)]
        neg_pairs = [(0,2), (0,3), (0,4), (1,2), (1,3), (1,4), (2,0), (2,1), (2,4), (3,0), (3,1), (3,4), (4,0), (4,1), (4,2), (4,3)]

        correct_total = 0
        for i in range(len(embeddings)):
            correct_pos_loss = 0
            correct_neg_loss = 0
            for a,p in pos_pairs:
                if a == i:
                    anchor, positive = embeddings[a], embeddings[p]
                    correct_pos_loss += torch.exp(torch.sqrt(torch.sum((anchor-positive)**2)))
            if correct_pos_loss > 0:
                correct_pos_loss = torch.log(correct_pos_loss)

            for a,n in neg_pairs:
                if a == i:
                    anchor, negative = embeddings[a], embeddings[n]
                    correct_neg_loss += torch.exp(neg_margin - torch.sqrt(torch.sum((anchor-negative)**2)))
            if correct_neg_loss > 0:
                correct_neg_loss = torch.log(correct_neg_loss)

            correct_total += torch.relu(correct_pos_loss + correct_neg_loss)

        correct_total /= embeddings.size(0)

        self.assertTrue(torch.isclose(loss, correct_total))


    def test_with_no_valid_pairs(self):
        loss_func = GeneralizedLiftedStructureLoss(neg_margin=0.5)
        embedding_angles = [0]
        embeddings = torch.tensor([c_f.angle_to_coord(a) for a in embedding_angles], requires_grad=True, dtype=torch.float) #2D embeddings
        labels = torch.LongTensor([0])
        loss = loss_func(embeddings, labels)
        loss.backward()
        self.assertEqual(loss, 0)