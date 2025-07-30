import torch

from anarcii.input_data_processing.tokeniser import NumberingTokeniser

from .model_loader import Loader
from .utils import dataloader


def first_index_above_threshold(preds, threshold=25):
    for i, val in enumerate(preds):
        if val > threshold:
            return i
    return None


class WindowFinder:
    def __init__(self, sequence_type, mode, batch_size, device):
        self.type = sequence_type.lower()
        self.mode = mode.lower()
        self.batch_size = batch_size
        self.device = device

        if self.type in ["antibody", "shark"]:
            self.sequence_tokeniser = NumberingTokeniser("protein_antibody")
            self.number_tokeniser = NumberingTokeniser("number_antibody")

        elif self.type == "tcr":
            self.sequence_tokeniser = NumberingTokeniser("protein_tcr")
            self.number_tokeniser = NumberingTokeniser("number_tcr")
        else:
            raise ValueError(f"Invalid model type: {self.type}")

        self.model = self._load_model()

    def _load_model(self):
        model_loader = Loader(self.type, self.mode, self.device)
        return model_loader.model

    def __call__(self, list_of_seqs, fallback: bool = False, scfv: bool = False):
        """
        Select the highest-scoring sequence.

        list_of_seqs: Sequences from whi, pdb_out_stem="blah"
        """
        dl = dataloader(self.batch_size, list_of_seqs)
        preds = []
        with torch.no_grad():
            for X in dl:
                src = X.to(self.device)
                batch_size = src.shape[0]

                src_mask = self.model.make_src_mask(src)
                enc_src = self.model.encoder(src, src_mask)
                input = src[:, 0].unsqueeze(1)

                trg_pad_mask, trg_causal_mask = self.model.make_trg_mask(input)
                output, _ = self.model.decoder(
                    input, enc_src, trg_pad_mask, trg_causal_mask, src_mask
                )
                likelihoods = output.topk(1, dim=2).values[:, 0]

                for batch_no in range(batch_size):
                    normalized_likelihood = likelihoods[batch_no, 0].item()
                    preds.append(normalized_likelihood)

            if scfv:
                #### DEBUG CMDS FOR SCFV DEV ####
                # plt.plot(preds)
                # plt.show()
                return preds

            # find first index over 25
            magic_number = first_index_above_threshold(preds, 25)

            # if nothing is over 25 then drop the threshold to 15 - next best.
            if not magic_number:
                magic_number = first_index_above_threshold(preds, 15)

            if magic_number is not None:
                return magic_number
            else:
                # Must be in window mode, the return max scoring window....
                return preds.index(max(preds)) if fallback else None
