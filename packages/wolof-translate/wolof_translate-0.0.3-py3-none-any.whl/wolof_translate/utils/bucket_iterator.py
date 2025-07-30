import numpy as np
from typing import Optional, List, Iterator, Union
from torch.utils.data import Sampler
from math import ceil
from tqdm import tqdm
import time

class SequenceLengthBatchSampler(Sampler[List[int]]):
    def __init__(
        self,
        dataset,
        boundaries: List[int],
        batch_sizes: List[int],
        input_key: Optional[int] = None,
        label_key: Optional[int] = None,
        drop_unique: bool = True,
    ):
        self.dataset = dataset
        self.boundaries = boundaries
        self.batch_sizes = batch_sizes
        self.drop_unique = drop_unique

        start_time = time.time()
        tqdm.write("Computing sequence lengths...")

        # Compute lengths with tqdm progress bar
        self.lengths = np.array([
            max(len(data[0]), len(data[2])) if input_key is None or label_key is None
            else max(len(data[input_key]), len(data[label_key]))
            for data in tqdm(dataset, desc="Lengths", unit="seq")
        ])

        tqdm.write(f"Sequence lengths computed in {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        tqdm.write("Assigning buckets...")

        # Assign bucket ids using digitize (vectorized)
        self.bucket_ids = np.digitize(self.lengths, bins=self.boundaries, right=True)

        # Create buckets of indices
        self.buckets = [np.where(self.bucket_ids == i)[0] for i in range(len(boundaries) + 1)]

        tqdm.write(f"Buckets assigned in {time.time() - start_time:.2f} seconds.")

        start_time = time.time()
        tqdm.write("Preparing batches...")

        # Prepare batches from buckets
        self.batches = []
        for bucket, batch_size in zip(self.buckets, self.batch_sizes):
            bucket = bucket.copy()
            np.random.shuffle(bucket)

            n_full_batches = len(bucket) // batch_size
            leftover = len(bucket) % batch_size

            for i in range(n_full_batches):
                batch = bucket[i * batch_size : (i + 1) * batch_size].tolist()
                self.batches.append(batch)

            if leftover > 0 and (leftover != 1 or not self.drop_unique):
                batch = bucket[-leftover:].tolist()
                self.batches.append(batch)

        self.length = len(self.batches)
        tqdm.write(f"Batches prepared in {time.time() - start_time:.2f} seconds.")

    def __iter__(self) -> Iterator[List[int]]:
        # Shuffle all batches globally to add randomness between buckets
        np.random.shuffle(self.batches)
        for batch in self.batches:
            yield batch

    def __len__(self) -> int:
        return self.length




# class SequenceLengthBatchSampler(Sampler[List[int]]):
#     def __init__(
#         self,
#         dataset,
#         boundaries: List[int],
#         batch_sizes: List[int],
#         input_key: Optional[int] = None,
#         label_key: Optional[int] = None,
#         drop_unique: bool = True,
#     ):
#         self.dataset = dataset
#         self.boundaries = boundaries
#         self.batch_sizes = batch_sizes
#         self.drop_unique = drop_unique
#         self.data_info = {}

#         # Extract lengths
#         for i in range(len(dataset)):
#             data = dataset[i]
#             if input_key is None or label_key is None:
#                 length = max(len(data[0]), len(data[2]))
#             else:
#                 length = max(len(data[input_key]), len(data[label_key]))
#             self.data_info[i] = {"index": i, "length": length}

#         self.calculate_length()

#     def calculate_length(self):
#         self.batches = []
#         sorted_indices = sorted(self.data_info.keys(), key=lambda i: self.data_info[i]["length"])

#         prev_boundary = 0
#         for boundary in self.boundaries:
#             batch = [i for i in sorted_indices if prev_boundary < self.data_info[i]["length"] <= boundary]
#             self.batches.append(batch)
#             sorted_indices = [i for i in sorted_indices if i not in batch]
#             prev_boundary = boundary

#         # Remaining sequences > last boundary
#         self.batches.append(sorted_indices)

#         total_batches = 0
#         for batch, batch_size in zip(self.batches, self.batch_sizes):
#             n_full_batches = len(batch) // batch_size
#             leftover = len(batch) % batch_size
#             total_batches += n_full_batches
#             if leftover > 0 and (leftover != 1 or not self.drop_unique):
#                 total_batches += 1
#         self.length = total_batches

#     def __iter__(self) -> Iterator[List[int]]:
#         for batch_indices, batch_size in zip(self.batches, self.batch_sizes):
#             num_batches = len(batch_indices) // batch_size

#             for i in range(num_batches):
#                 current_bucket = batch_indices[i * batch_size: (i + 1) * batch_size]
#                 np.random.shuffle(current_bucket)
#                 yield [self.data_info[idx]["index"] for idx in current_bucket]

#             remaining = len(batch_indices) % batch_size
#             if remaining > 0 and (remaining != 1 or not self.drop_unique):
#                 current_bucket = batch_indices[-remaining:]
#                 np.random.shuffle(current_bucket)
#                 yield [self.data_info[idx]["index"] for idx in current_bucket]

#     def __len__(self) -> int:
#         return self.length



class BucketSampler(Sampler):
    def __init__(self, dataset, batch_size, sort_key=lambda x, index_1, index_2: max(len(x[index_1]), len(x[index_2])), input_key: Union[str, int] = 0, label_key: Union[str, int] = 1):
        self.dataset = dataset
        self.batch_size = batch_size
        self.sort_key = sort_key
        self.index_1 = input_key
        self.index_2 = label_key
        indices = np.argsort([self.sort_key(self.dataset[i], self.index_1, self.index_2) for i in range(len(self.dataset))])
        self.batches = [indices[i:i + self.batch_size] for i in range(0, len(indices), self.batch_size)]

    def __iter__(self):
        if self.batch_size > 1:
            np.random.shuffle(self.batches)
        for batch in self.batches:
            yield batch.tolist()

    def __len__(self):
        return ceil(len(self.dataset) / self.batch_size)


def collate_fn(batch):
    from torch.nn.utils.rnn import pad_sequence
    # Separate the input sequences, target sequences, and attention masks
    input_seqs, input_masks, target_seqs, target_masks = zip(*batch)

    # Pad the input sequences to have the same length
    padded_input_seqs = pad_sequence(input_seqs, batch_first=True)

    # Pad the target sequences to have the same length
    padded_target_seqs = pad_sequence(target_seqs, batch_first=True)

    # Pad the input masks to have the same length
    padded_input_masks = pad_sequence(input_masks, batch_first=True)

    # Pad the labels masks to have the same length
    padded_target_masks = pad_sequence(target_masks, batch_first=True)

    return padded_input_seqs, padded_input_masks, padded_target_seqs, padded_target_masks

def collate_fn_trunc(batch, max_len, eos_token_id, pad_token_id):
    from torch.nn.utils.rnn import pad_sequence
    # Separate the input sequences, target sequences, and attention masks
    input_seqs, input_masks, target_seqs, target_masks = zip(*batch)

    # Pad the input sequences to have the same length
    padded_input_seqs = pad_sequence(input_seqs, batch_first=True)[:,:max_len]

    # Pad the target sequences to have the same length
    padded_target_seqs = pad_sequence(target_seqs, batch_first=True)[:,:max_len]
    
    # add eos_token id if pad token id is not visible
    padded_input_seqs[:, -1:][(padded_input_seqs[:, -1:] != eos_token_id) & (padded_input_seqs[:, -1:] != pad_token_id)] = eos_token_id
    
    padded_target_seqs[:, -1:][(padded_target_seqs[:, -1:] != eos_token_id) & (padded_target_seqs[:, -1:] != pad_token_id)] = eos_token_id 

    # Pad the input masks to have the same length
    padded_input_masks = pad_sequence(input_masks, batch_first=True)[:,:max_len]

    # Pad the labels masks to have the same length
    padded_target_masks = pad_sequence(target_masks, batch_first=True)[:,:max_len]

    return padded_input_seqs, padded_input_masks, padded_target_seqs, padded_target_masks
