This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: packages.json, **/terraform.tfstate, **/terraform.tfstate.backup
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
parakeet_mlx/
  __init__.py
  alignment.py
  attention.py
  audio.py
  cache.py
  cli.py
  conformer.py
  ctc.py
  parakeet.py
  rnnt.py
  tokenizer.py
  utils.py
.gitignore
LICENSE
pyproject.toml
README.md
```

# Files

## File: parakeet_mlx/ctc.py
````python
from dataclasses import dataclass

import mlx.core as mx
import mlx.nn as nn


@dataclass
class ConvASRDecoderArgs:
    feat_in: int
    num_classes: int
    vocabulary: list[str]


@dataclass
class AuxCTCArgs:
    decoder: ConvASRDecoderArgs


class ConvASRDecoder(nn.Module):
    def __init__(self, args: ConvASRDecoderArgs):
        super().__init__()

        args.num_classes = (
            len(args.vocabulary) if args.num_classes <= 0 else args.num_classes
        ) + 1

        self.decoder_layers = [
            nn.Conv1d(args.feat_in, args.num_classes, kernel_size=1, bias=True)
        ]

        self.temperature = 1.0  # change manually if desired

    def __call__(self, x: mx.array) -> mx.array:
        return nn.log_softmax(self.decoder_layers[0](x) / self.temperature)
````

## File: parakeet_mlx/tokenizer.py
````python
# decode some tokens (might edit it if to support other varients)
def decode(tokens: list[int], vocabulary: list[str]):
    return "".join([vocabulary[token].replace("▁", " ") for token in tokens])
````

## File: .gitignore
````
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv
.python-version

# uv
uv.lock

# mac
.DS_Store
````

## File: LICENSE
````
Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
````

## File: parakeet_mlx/rnnt.py
````python
from dataclasses import dataclass

import mlx.core as mx
import mlx.nn as nn


@dataclass
class PredictNetworkArgs:
    pred_hidden: int
    pred_rnn_layers: int
    rnn_hidden_size: int | None = None


@dataclass
class JointNetworkArgs:
    joint_hidden: int
    activation: str
    encoder_hidden: int
    pred_hidden: int


@dataclass
class PredictArgs:
    blank_as_pad: bool
    vocab_size: int
    prednet: PredictNetworkArgs


@dataclass
class JointArgs:
    num_classes: int
    vocabulary: list[str]
    jointnet: JointNetworkArgs
    num_extra_outputs: int = 0


class LSTM(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int = 1,
        bias: bool = True,
        batch_first: bool = True,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.lstm = [
            nn.LSTM(input_size if i == 0 else hidden_size, hidden_size, bias=bias)
            for i in range(num_layers)
        ]

    def __call__(
        self, x: mx.array, h_c: tuple[mx.array, mx.array] | None = None
    ) -> tuple[mx.array, tuple[mx.array, mx.array]]:
        if self.batch_first:
            x = mx.transpose(x, (1, 0, 2))

        if h_c is None:
            h = [None] * self.num_layers
            c = [None] * self.num_layers
        else:
            h, c = h_c

        outputs = x
        next_h = []
        next_c = []

        for i in range(self.num_layers):
            layer = self.lstm[i]

            all_h_steps, all_c_steps = layer(outputs, hidden=h[i], cell=c[i])
            outputs = all_h_steps
            next_h.append(all_h_steps[-1])
            next_c.append(all_c_steps[-1])

        if self.batch_first:
            outputs = mx.transpose(outputs, (1, 0, 2))

        final_h = mx.stack(next_h, axis=0)
        final_c = mx.stack(next_c, axis=0)

        return outputs, (final_h, final_c)


class PredictNetwork(nn.Module):
    def __init__(self, args: PredictArgs):
        super().__init__()

        self.pred_hidden = args.prednet.pred_hidden

        self.prediction = {
            "embed": nn.Embedding(
                args.vocab_size if not args.blank_as_pad else args.vocab_size + 1,
                args.prednet.pred_hidden,
            ),
            "dec_rnn": LSTM(
                args.prednet.pred_hidden,
                args.prednet.rnn_hidden_size
                if args.prednet.rnn_hidden_size
                else args.prednet.pred_hidden,
                args.prednet.pred_rnn_layers,
            ),
        }

    def __call__(
        self, y: mx.array | None, h_c: tuple[mx.array, mx.array] | None = None
    ) -> tuple[mx.array, tuple[mx.array, mx.array]]:
        if y is not None:
            embedded_y = self.prediction["embed"](y)
        else:
            batch = 1 if h_c is None else h_c[0].shape[1]
            embedded_y = mx.zeros((batch, 1, self.pred_hidden))
        return self.prediction["dec_rnn"](embedded_y, h_c)


class JointNetwork(nn.Module):
    def __init__(self, args: JointArgs):
        super().__init__()
        self._num_classes = args.num_classes + 1 + args.num_extra_outputs

        if args.jointnet.activation not in ["relu", "sigmoid", "tanh"]:
            raise ValueError(
                "Unsupported activation for joint step - please pass one of "
                "[relu, sigmoid, tanh]"
            )

        activation = args.jointnet.activation.lower()

        if activation == "relu":
            activation = nn.ReLU()
        elif activation == "sigmoid":
            activation = nn.Sigmoid()
        else:
            activation = nn.Tanh()

        self.pred = nn.Linear(args.jointnet.pred_hidden, args.jointnet.joint_hidden)
        self.enc = nn.Linear(args.jointnet.encoder_hidden, args.jointnet.joint_hidden)
        self.joint_net = [activation] + [
            nn.Identity(),
            nn.Linear(args.jointnet.joint_hidden, self._num_classes),
        ]

    def __call__(self, enc: mx.array, pred: mx.array) -> mx.array:
        enc = self.enc(enc)
        pred = self.pred(pred)

        x = mx.expand_dims(enc, 2) + mx.expand_dims(pred, 1)

        for layer in self.joint_net:
            x = layer(x)

        return x
````

## File: parakeet_mlx/__init__.py
````python
from parakeet_mlx.alignment import AlignedResult, AlignedSentence, AlignedToken
from parakeet_mlx.parakeet import DecodingConfig, ParakeetTDT, ParakeetTDTArgs
from parakeet_mlx.utils import from_pretrained

__all__ = [
    "DecodingConfig",
    "ParakeetTDTArgs",
    "ParakeetTDT",
    "from_pretrained",
    "AlignedResult",
    "AlignedSentence",
    "AlignedToken",
]
````

## File: parakeet_mlx/cache.py
````python
import mlx.core as mx


class ConformerCache:
    keys: mx.array | None
    values: mx.array | None
    conv: mx.array | None

    offset: int
    step = 256

    def __init__(self):
        self.keys = None
        self.values = None
        self.conv = None
        self.offset = 0

    def update_and_fetch_kv(
        self, keys: mx.array, values: mx.array
    ) -> tuple[mx.array, mx.array]:
        # k, v is [batch, head, seq, dim]
        prev = self.offset
        if (
            self.keys is None
            or self.values is None
            or (prev + keys.shape[2]) > self.keys.shape[2]
        ):
            B, H, S, D_KEYS = keys.shape
            _, _, _, D_VALUES = values.shape
            S_CACHE = ((self.step + S - 1) // self.step) * self.step

            new_k = mx.zeros((B, H, S_CACHE, D_KEYS), keys.dtype)
            new_v = mx.zeros((B, H, S_CACHE, D_VALUES), keys.dtype)

            if self.keys is None or self.values is None:  # type safety!
                self.keys, self.values = new_k, new_v
            else:
                if prev % self.step != 0:
                    self.keys = self.keys[..., :prev, :]
                    self.values = self.values[..., :prev, :]
                self.keys = mx.concatenate([self.keys, new_k], axis=2)
                self.values = mx.concatenate([self.values, new_v], axis=2)

        self.offset += keys.shape[2]
        self.keys[..., prev : self.offset, :] = keys
        self.values[..., prev : self.offset, :] = values

        return self.keys[..., : self.offset, :], self.values[..., : self.offset, :]

    def update_and_fetch_conv(self, x: mx.array, padding: int = 0) -> mx.array:
        if padding == 0:
            return x

        B, S, D = x.shape

        if self.conv is None:
            self.conv = mx.zeros((B, padding, D), x.dtype)

        tokens_to_cache = min(padding, S)

        cache_update = x[:, S - tokens_to_cache : S, :]

        if tokens_to_cache < padding:
            self.conv = mx.concatenate(
                [self.conv[:, tokens_to_cache:, :], cache_update], axis=1
            )
        else:
            self.conv = cache_update

        result = mx.concatenate([self.conv, x], axis=1)
        result = mx.pad(result, ((0, 0), (0, padding)))

        return result


class RotatingConformerCache(ConformerCache):
    capacity: int
    cache_drop_size: int

    def __init__(self, capacity: int, cache_drop_size: int = 0):
        super().__init__()

        self.capacity = capacity
        self.cache_drop_size = cache_drop_size

    def _ring_append(self, buf: mx.array, new: mx.array):
        C = self.capacity
        pos = self.offset % C
        T = new.shape[2]
        first = min(T, C - pos)
        buf[..., pos : pos + first, :] = new[..., :first, :]
        if T > first:
            buf[..., : T - first, :] = new[..., first:, :]

    def update_and_fetch_kv(self, keys: mx.array, values: mx.array):
        B, H, S, D = keys.shape

        if self.keys is None or self.values is None:
            self.keys = mx.zeros((B, H, self.capacity, D), keys.dtype)
            self.values = mx.zeros((B, H, self.capacity, D), keys.dtype)

        if self.offset < self.capacity:
            hist_k = self.keys[..., : self.offset, :]
            hist_v = self.values[..., : self.offset, :]
        else:
            shift = -(self.offset % self.capacity)
            hist_k = mx.roll(self.keys, shift, 2)
            hist_v = mx.roll(self.values, shift, 2)

        k_out = mx.concatenate([hist_k, keys], axis=2)
        v_out = mx.concatenate([hist_v, values], axis=2)

        drop = self.cache_drop_size
        to_cache = min(max(0, S - drop), self.capacity)

        if to_cache > 0:
            k_chunk = keys[
                ...,
                S - self.cache_drop_size - to_cache : S - self.cache_drop_size,
                :,
            ]
            v_chunk = values[
                ...,
                S - self.cache_drop_size - to_cache : S - self.cache_drop_size,
                :,
            ]
            self._ring_append(self.keys, k_chunk)
            self._ring_append(self.values, v_chunk)
            self.offset += to_cache

        return k_out, v_out

    def update_and_fetch_conv(self, x: mx.array, padding: int = 0) -> mx.array:
        if padding == 0:
            return x

        B, S, D = x.shape

        if self.conv is None:
            self.conv = mx.zeros((B, padding, D), x.dtype)

        if S > self.cache_drop_size:
            tokens_to_cache = min(padding, S - self.cache_drop_size)
            cache_update = x[:, S - tokens_to_cache : S, :]

            if tokens_to_cache < padding:
                self.conv = mx.concatenate(
                    [self.conv[:, tokens_to_cache:, :], cache_update], axis=1
                )
            else:
                self.conv = cache_update

        result = mx.concatenate([self.conv, x], axis=1)
        result = mx.pad(result, ((0, 0), (0, padding), (0, 0)))

        return result
````

## File: parakeet_mlx/alignment.py
````python
from dataclasses import dataclass


@dataclass
class AlignedToken:
    id: int
    text: str
    start: float
    duration: float
    end: float = 0.0  # temporary

    def __post_init__(self) -> None:
        self.end = self.start + self.duration


@dataclass
class AlignedSentence:
    text: str
    tokens: list[AlignedToken]
    start: float = 0.0  # temporary
    end: float = 0.0  # temporary
    duration: float = 0.0  # temporary

    def __post_init__(self) -> None:
        self.tokens = list(sorted(self.tokens, key=lambda x: x.start))
        self.start = self.tokens[0].start
        self.end = self.tokens[-1].end
        self.duration = self.end - self.start


@dataclass
class AlignedResult:
    text: str
    sentences: list[AlignedSentence]

    def __post_init__(self) -> None:
        self.text = self.text.strip()

    @property
    def tokens(self) -> list[AlignedToken]:
        return [token for sentence in self.sentences for token in sentence.tokens]


def tokens_to_sentences(tokens: list[AlignedToken]) -> list[AlignedSentence]:
    sentences = []
    current_tokens = []

    for idx, token in enumerate(tokens):
        current_tokens.append(token)

        # hacky, will fix
        if (
            "!" in token.text
            or "?" in token.text
            or "。" in token.text
            or "？" in token.text
            or "！" in token.text
            or (
                "." in token.text
                and (idx == len(tokens) - 1 or " " in tokens[idx + 1].text)
            )
        ):  # type: ignore
            sentence_text = "".join(t.text for t in current_tokens)
            sentence = AlignedSentence(text=sentence_text, tokens=current_tokens)
            sentences.append(sentence)

            current_tokens = []

    if current_tokens:
        sentence_text = "".join(t.text for t in current_tokens)
        sentence = AlignedSentence(text=sentence_text, tokens=current_tokens)
        sentences.append(sentence)

    return sentences


def sentences_to_result(sentences: list[AlignedSentence]) -> AlignedResult:
    return AlignedResult("".join(sentence.text for sentence in sentences), sentences)


def merge_longest_contiguous(
    a: list[AlignedToken],
    b: list[AlignedToken],
    *,
    overlap_duration: float,
):
    if not a or not b:
        return b if not a else a

    a_end_time = a[-1].end
    b_start_time = b[0].start

    if a_end_time <= b_start_time:
        return a + b

    overlap_a = [token for token in a if token.end > b_start_time - overlap_duration]
    overlap_b = [token for token in b if token.start < a_end_time + overlap_duration]

    enough_pairs = len(overlap_a) // 2

    if len(overlap_a) < 2 or len(overlap_b) < 2:
        cutoff_time = (a_end_time + b_start_time) / 2
        return [t for t in a if t.end <= cutoff_time] + [
            t for t in b if t.start >= cutoff_time
        ]

    best_contiguous = []
    for i in range(len(overlap_a)):
        for j in range(len(overlap_b)):
            if (
                overlap_a[i].id == overlap_b[j].id
                and abs(overlap_a[i].start - overlap_b[j].start) < overlap_duration / 2
            ):
                current = []
                k, l = i, j
                while (
                    k < len(overlap_a)
                    and l < len(overlap_b)
                    and overlap_a[k].id == overlap_b[l].id
                    and abs(overlap_a[k].start - overlap_b[l].start)
                    < overlap_duration / 2
                ):
                    current.append((k, l))
                    k += 1
                    l += 1

                if len(current) > len(best_contiguous):
                    best_contiguous = current

    if len(best_contiguous) >= enough_pairs:
        a_start_idx = len(a) - len(overlap_a)
        lcs_indices_a = [a_start_idx + pair[0] for pair in best_contiguous]
        lcs_indices_b = [pair[1] for pair in best_contiguous]

        result = []
        result.extend(a[: lcs_indices_a[0]])

        for i in range(len(best_contiguous)):
            idx_a = lcs_indices_a[i]
            idx_b = lcs_indices_b[i]

            result.append(a[idx_a])

            if i < len(best_contiguous) - 1:
                next_idx_a = lcs_indices_a[i + 1]
                next_idx_b = lcs_indices_b[i + 1]

                gap_tokens_a = a[idx_a + 1 : next_idx_a]
                gap_tokens_b = b[idx_b + 1 : next_idx_b]

                if len(gap_tokens_b) > len(gap_tokens_a):
                    result.extend(gap_tokens_b)
                else:
                    result.extend(gap_tokens_a)

        result.extend(b[lcs_indices_b[-1] + 1 :])
        return result
    else:
        raise RuntimeError(f"No pairs exceeding {enough_pairs}")


def merge_longest_common_subsequence(
    a: list[AlignedToken],
    b: list[AlignedToken],
    *,
    overlap_duration: float,
):
    if not a or not b:
        return b if not a else a

    a_end_time = a[-1].end
    b_start_time = b[0].start

    if a_end_time <= b_start_time:
        return a + b

    overlap_a = [token for token in a if token.end > b_start_time - overlap_duration]
    overlap_b = [token for token in b if token.start < a_end_time + overlap_duration]

    if len(overlap_a) < 2 or len(overlap_b) < 2:
        cutoff_time = (a_end_time + b_start_time) / 2
        return [t for t in a if t.end <= cutoff_time] + [
            t for t in b if t.start >= cutoff_time
        ]

    dp = [[0 for _ in range(len(overlap_b) + 1)] for _ in range(len(overlap_a) + 1)]

    for i in range(1, len(overlap_a) + 1):
        for j in range(1, len(overlap_b) + 1):
            if (
                overlap_a[i - 1].id == overlap_b[j - 1].id
                and abs(overlap_a[i - 1].start - overlap_b[j - 1].start)
                < overlap_duration / 2
            ):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    lcs_pairs = []
    i, j = len(overlap_a), len(overlap_b)

    while i > 0 and j > 0:
        if (
            overlap_a[i - 1].id == overlap_b[j - 1].id
            and abs(overlap_a[i - 1].start - overlap_b[j - 1].start)
            < overlap_duration / 2
        ):
            lcs_pairs.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    lcs_pairs.reverse()

    if not lcs_pairs:
        cutoff_time = (a_end_time + b_start_time) / 2
        return [t for t in a if t.end <= cutoff_time] + [
            t for t in b if t.start >= cutoff_time
        ]

    a_start_idx = len(a) - len(overlap_a)
    lcs_indices_a = [a_start_idx + pair[0] for pair in lcs_pairs]
    lcs_indices_b = [pair[1] for pair in lcs_pairs]

    result = []

    result.extend(a[: lcs_indices_a[0]])

    for i in range(len(lcs_pairs)):
        idx_a = lcs_indices_a[i]
        idx_b = lcs_indices_b[i]

        result.append(a[idx_a])

        if i < len(lcs_pairs) - 1:
            next_idx_a = lcs_indices_a[i + 1]
            next_idx_b = lcs_indices_b[i + 1]

            gap_tokens_a = a[idx_a + 1 : next_idx_a]
            gap_tokens_b = b[idx_b + 1 : next_idx_b]

            if len(gap_tokens_b) > len(gap_tokens_a):
                result.extend(gap_tokens_b)
            else:
                result.extend(gap_tokens_a)

    result.extend(b[lcs_indices_b[-1] + 1 :])

    return result
````

## File: parakeet_mlx/utils.py
````python
import json
from pathlib import Path

import mlx.core as mx
from dacite import from_dict
from huggingface_hub import hf_hub_download
from mlx.utils import tree_flatten, tree_unflatten

from parakeet_mlx.parakeet import (
    BaseParakeet,
    ParakeetCTC,
    ParakeetCTCArgs,
    ParakeetRNNT,
    ParakeetRNNTArgs,
    ParakeetTDT,
    ParakeetTDTArgs,
    ParakeetTDTCTC,
    ParakeetTDTCTCArgs,
)


def from_config(config: dict) -> BaseParakeet:
    """Loads model from config (randomized weight)"""
    if (
        config.get("target")
        == "nemo.collections.asr.models.rnnt_bpe_models.EncDecRNNTBPEModel"
        and config.get("model_defaults", {}).get("tdt_durations") is not None
    ):
        cfg = from_dict(ParakeetTDTArgs, config)
        model = ParakeetTDT(cfg)
    elif (
        config.get("target")
        == "nemo.collections.asr.models.hybrid_rnnt_ctc_bpe_models.EncDecHybridRNNTCTCBPEModel"
        and config.get("model_defaults", {}).get("tdt_durations") is not None
    ):
        cfg = from_dict(ParakeetTDTCTCArgs, config)
        model = ParakeetTDTCTC(cfg)
    elif (
        config.get("target")
        == "nemo.collections.asr.models.rnnt_bpe_models.EncDecRNNTBPEModel"
        and config.get("model_defaults", {}).get("tdt_durations") is None
    ):
        cfg = from_dict(ParakeetRNNTArgs, config)
        model = ParakeetRNNT(cfg)
    elif (
        config.get("target")
        == "nemo.collections.asr.models.ctc_bpe_models.EncDecCTCModelBPE"
    ):
        cfg = from_dict(ParakeetCTCArgs, config)
        model = ParakeetCTC(cfg)
    else:
        raise ValueError("Model is not supported yet!")

    model.eval()  # prevents layernorm not computing correctly on inference!

    return model


def from_pretrained(
    hf_id_or_path: str, *, dtype: mx.Dtype = mx.bfloat16
) -> BaseParakeet:
    """Loads model from Hugging Face or local directory"""
    try:
        config = json.load(open(hf_hub_download(hf_id_or_path, "config.json"), "r"))
        weight = hf_hub_download(hf_id_or_path, "model.safetensors")
    except Exception:
        config = json.load(open(Path(hf_id_or_path) / "config.json", "r"))
        weight = str(Path(hf_id_or_path) / "model.safetensors")

    model = from_config(config)
    model.load_weights(weight)

    # cast dtype
    curr_weights = dict(tree_flatten(model.parameters()))
    curr_weights = [(k, v.astype(dtype)) for k, v in curr_weights.items()]
    model.update(tree_unflatten(curr_weights))

    return model
````

## File: parakeet_mlx/cli.py
````python
import datetime
import json
from pathlib import Path
from typing import Any, Dict, List

import typer
from mlx.core import bfloat16, float32
from rich import print
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from typing_extensions import Annotated

from parakeet_mlx import AlignedResult, AlignedSentence, AlignedToken, from_pretrained

app = typer.Typer(no_args_is_help=True)


# helpers
def format_timestamp(
    seconds: float, always_include_hours: bool = True, decimal_marker: str = ","
) -> str:
    assert seconds >= 0
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    seconds = milliseconds // 1_000
    milliseconds %= 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return (
        f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"
    )


def to_txt(result: AlignedResult) -> str:
    """Format transcription result as plain text."""
    return result.text.strip()


def to_srt(result: AlignedResult, highlight_words: bool = False) -> str:
    """
    Format transcription result as an SRT file.
    """
    srt_content = []
    entry_index = 1
    if highlight_words:
        for sentence in result.sentences:
            for i, token in enumerate(sentence.tokens):
                start_time = format_timestamp(token.start, decimal_marker=",")
                end_time = format_timestamp(
                    token.end
                    if token == sentence.tokens[-1]
                    else sentence.tokens[i + 1].start,
                    decimal_marker=",",
                )

                text = ""
                for j, inner_token in enumerate(sentence.tokens):
                    if i == j:
                        text += inner_token.text.replace(
                            inner_token.text.strip(),
                            f"<u>{inner_token.text.strip()}</u>",
                        )
                    else:
                        text += inner_token.text
                text.strip()

                srt_content.append(f"{entry_index}")
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(text)
                srt_content.append("")
                entry_index += 1
    else:
        for sentence in result.sentences:
            start_time = format_timestamp(sentence.start, decimal_marker=",")
            end_time = format_timestamp(sentence.end, decimal_marker=",")
            text = sentence.text.strip()

            srt_content.append(f"{entry_index}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(text)
            srt_content.append("")
            entry_index += 1

    return "\n".join(srt_content)


def to_vtt(result: AlignedResult, highlight_words: bool = False) -> str:
    """
    Format transcription result as a VTT file.
    """
    vtt_content = ["WEBVTT", ""]
    if highlight_words:
        for sentence in result.sentences:
            for i, token in enumerate(sentence.tokens):
                start_time = format_timestamp(token.start, decimal_marker=".")
                end_time = format_timestamp(
                    token.end
                    if token == sentence.tokens[-1]
                    else sentence.tokens[i + 1].start,
                    decimal_marker=".",
                )

                text_line = ""
                for j, inner_token in enumerate(sentence.tokens):
                    if i == j:
                        text_line += inner_token.text.replace(
                            inner_token.text.strip(),
                            f"<b>{inner_token.text.strip()}</b>",
                        )
                    else:
                        text_line += inner_token.text
                text_line = text_line.strip()

                vtt_content.append(f"{start_time} --> {end_time}")
                vtt_content.append(text_line)
                vtt_content.append("")
    else:
        for sentence in result.sentences:
            start_time = format_timestamp(sentence.start, decimal_marker=".")
            end_time = format_timestamp(sentence.end, decimal_marker=".")
            text_line = sentence.text.strip()

            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(text_line)
            vtt_content.append("")

    return "\n".join(vtt_content)


def _aligned_token_to_dict(token: AlignedToken) -> Dict[str, Any]:
    return {
        "text": token.text,
        "start": round(token.start, 3),
        "end": round(token.end, 3),
        "duration": round(token.duration, 3),
    }


def _aligned_sentence_to_dict(sentence: AlignedSentence) -> Dict[str, Any]:
    return {
        "text": sentence.text,
        "start": round(sentence.start, 3),
        "end": round(sentence.end, 3),
        "duration": round(sentence.duration, 3),
        "tokens": [_aligned_token_to_dict(token) for token in sentence.tokens],
    }


def to_json(result: AlignedResult) -> str:
    output_dict = {
        "text": result.text,
        "sentences": [
            _aligned_sentence_to_dict(sentence) for sentence in result.sentences
        ],
    }
    return json.dumps(output_dict, indent=2, ensure_ascii=False)


@app.command("transcribe")
def transcribe(
    audios: Annotated[
        List[Path],
        typer.Argument(
            help="Files to transcribe",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    model: Annotated[
        str, typer.Option(help="Hugging Face repository of model to use")
    ] = "mlx-community/parakeet-tdt-0.6b-v2",
    output_dir: Annotated[
        Path, typer.Option(help="Directory to save transcriptions")
    ] = Path("."),
    output_format: Annotated[
        str, typer.Option(help="Format for output files (txt, srt, vtt, json, all)")
    ] = "srt",
    output_template: Annotated[
        str,
        typer.Option(
            help="Template for output filenames, e.g. '{filename}_{date}_{index}'"
        ),
    ] = "{filename}",
    highlight_words: Annotated[
        bool,
        typer.Option(help="Underline/timestamp each word as it is spoken in srt/vtt"),
    ] = False,
    chunk_duration: Annotated[
        float,
        typer.Option(
            help="Chunking duration in seconds for long audio, 0 to disable chunking."
        ),
    ] = 60 * 2,
    overlap_duration: Annotated[
        float, typer.Option(help="Overlap duration in seconds if using chunking")
    ] = 15,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print out process and debug messages"),
    ] = False,
    fp32: Annotated[
        bool, typer.Option("--fp32/--bf16", help="Use FP32 precision")
    ] = False,
):
    """
    Transcribe audio files using Parakeet MLX models.
    """
    if verbose:
        print(f"Loading model: [bold cyan]{model}[/bold cyan]...")

    try:
        loaded_model = from_pretrained(model, dtype=bfloat16 if not fp32 else float32)
        if verbose:
            print("[green]Model loaded successfully.[/green]")
    except Exception as e:
        print(f"[bold red]Error loading model {model}:[/bold red] {e}")
        raise typer.Exit(code=1)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[bold red]Error creating output directory {output_dir}:[/bold red] {e}")
        raise typer.Exit(code=1)

    if verbose:
        print(f"Output directory: [bold cyan]{output_dir.resolve()}[/bold cyan]")
        print(f"Output format(s): [bold cyan]{output_format}[/bold cyan]")
        if output_format in ["srt", "vtt", "all"] and highlight_words:
            print("Highlight words: [bold cyan]Enabled[/bold cyan]")

    formatters = {
        "txt": to_txt,
        "srt": lambda r: to_srt(r, highlight_words=highlight_words),
        "vtt": lambda r: to_vtt(r, highlight_words=highlight_words),
        "json": to_json,
    }

    formats_to_generate = []
    if output_format == "all":
        formats_to_generate = list(formatters.keys())
    elif output_format in formatters:
        formats_to_generate = [output_format]
    else:
        print(
            f"[bold red]Error: Invalid output format '{output_format}'. Choose from {list(formatters.keys()) + ['all']}.[/bold red]"
        )
        raise typer.Exit(code=1)

    total_files = len(audios)
    if verbose:
        print(f"Transcribing {total_files} file(s)...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Transcribing...", total=total_files)

        for i, audio_path in enumerate(audios):
            if verbose:
                print(
                    f"\nProcessing file {i + 1}/{total_files}: [bold cyan]{audio_path.name}[/bold cyan]"
                )
            else:
                progress.update(
                    task, description=f"Processing [cyan]{audio_path.name}[/cyan]..."
                )

            try:
                result: AlignedResult = loaded_model.transcribe(
                    audio_path,
                    dtype=bfloat16 if not fp32 else float32,
                    chunk_duration=chunk_duration if chunk_duration != 0 else None,
                    overlap_duration=overlap_duration,
                    chunk_callback=lambda current, full: progress.update(
                        task, total=total_files * full, completed=full * i + current
                    ),
                )

                if verbose:
                    for sentence in result.sentences:
                        start, end, text = sentence.start, sentence.end, sentence.text
                        line = f"[blue][{format_timestamp(start)} --> {format_timestamp(end)}][/blue] {text.strip()}"
                        print(line)

                base_filename = audio_path.stem
                template_vars = {
                    "filename": base_filename,
                    "date": datetime.datetime.now().strftime("%Y%m%d"),
                    "index": str(i + 1),
                }

                output_basename = output_template.format(**template_vars)

                for fmt in formats_to_generate:
                    formatter = formatters[fmt]
                    output_content = formatter(result)
                    output_filename = f"{output_basename}.{fmt}"
                    output_filepath = output_dir / output_filename

                    try:
                        with open(output_filepath, "w", encoding="utf-8") as f:
                            f.write(output_content)
                        if verbose:
                            print(
                                f"[green]Saved {fmt.upper()}:[/green] {output_filepath.absolute()}"
                            )
                    except Exception as e:
                        print(
                            f"[bold red]Error writing output file {output_filepath}:[/bold red] {e}"
                        )

            except Exception as e:
                print(f"[bold red]Error transcribing file {audio_path}:[/bold red] {e}")

            progress.update(task, total=total_files, completed=i + 1)

    print(
        f"\n[bold green]Transcription complete.[/bold green] Outputs saved in '{output_dir.resolve()}'."
    )


if __name__ == "__main__":
    app()
````

## File: parakeet_mlx/conformer.py
````python
import math
from dataclasses import dataclass
from typing import Literal, Optional

import mlx.core as mx
import mlx.nn as nn
from mlx.nn.utils import tree_flatten

from parakeet_mlx.attention import (
    LocalRelPositionalEncoding,
    MultiHeadAttention,
    RelPositionalEncoding,
    RelPositionMultiHeadAttention,
    RelPositionMultiHeadLocalAttention,
)


@dataclass
class ConformerArgs:
    feat_in: int  # mel-log
    n_layers: int
    d_model: int
    n_heads: int
    ff_expansion_factor: int
    subsampling_factor: int
    self_attention_model: str
    subsampling: str
    conv_kernel_size: int
    subsampling_conv_channels: int
    pos_emb_max_len: int
    causal_downsampling: bool = False
    use_bias: bool = True
    xscaling: bool = False
    pos_bias_u: Optional[mx.array] = None
    pos_bias_v: Optional[mx.array] = None
    subsampling_conv_chunking_factor: int = 1
    att_context_size: Optional[list[int]] = None


class FeedForward(nn.Module):
    def __init__(self, d_model: int, d_ff: int, use_bias: bool = True):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff, bias=use_bias)
        self.activation = nn.SiLU()
        self.linear2 = nn.Linear(d_ff, d_model, bias=use_bias)

    def __call__(self, x: mx.array) -> mx.array:
        return self.linear2(self.activation(self.linear1(x)))


class Convolution(nn.Module):
    def __init__(self, args: ConformerArgs):
        assert (args.conv_kernel_size - 1) % 2 == 0
        super().__init__()

        self.padding = (args.conv_kernel_size - 1) // 2

        self.pointwise_conv1 = nn.Conv1d(
            args.d_model,
            args.d_model * 2,
            kernel_size=1,
            stride=1,
            padding=0,
            bias=args.use_bias,
        )
        self.depthwise_conv = nn.Conv1d(
            args.d_model,
            args.d_model,
            kernel_size=args.conv_kernel_size,
            stride=1,
            padding=0,
            groups=args.d_model,
            bias=args.use_bias,
        )
        self.batch_norm = nn.BatchNorm(args.d_model)
        self.activation = nn.SiLU()
        self.pointwise_conv2 = nn.Conv1d(
            args.d_model,
            args.d_model,
            kernel_size=1,
            stride=1,
            padding=0,
            bias=args.use_bias,
        )

    def __call__(self, x: mx.array, cache=None) -> mx.array:
        # x = x.swapaxes(1, 2)

        x = self.pointwise_conv1(x)
        x = nn.glu(x, axis=2)  # might make it variable later

        # caching for conv!
        if cache is not None:
            x = cache.update_and_fetch_conv(x, padding=self.padding)
        else:
            x = mx.pad(x, ((0, 0), (self.padding, self.padding), (0, 0)))
        x = self.depthwise_conv(x)

        x = self.batch_norm(x)
        x = self.activation(x)
        x = self.pointwise_conv2(x)

        return x


class ConformerBlock(nn.Module):
    def __init__(self, args: ConformerArgs):
        super().__init__()
        ff_hidden_dim = args.d_model * args.ff_expansion_factor

        self.args = args

        self.norm_feed_forward1 = nn.LayerNorm(args.d_model)
        self.feed_forward1 = FeedForward(args.d_model, ff_hidden_dim, args.use_bias)

        self.norm_self_att = nn.LayerNorm(args.d_model)
        self.self_attn = (
            RelPositionMultiHeadAttention(
                args.n_heads,
                args.d_model,
                bias=args.use_bias,
                pos_bias_u=args.pos_bias_u,
                pos_bias_v=args.pos_bias_v,
            )
            if args.self_attention_model == "rel_pos"
            else RelPositionMultiHeadLocalAttention(
                args.n_heads,
                args.d_model,
                bias=args.use_bias,
                pos_bias_u=args.pos_bias_u,
                pos_bias_v=args.pos_bias_v,
                context_size=(args.att_context_size[0], args.att_context_size[1])
                if args.att_context_size is not None
                else (-1, -1),
            )
            if args.self_attention_model == "rel_pos_local_attn"
            else MultiHeadAttention(
                args.n_heads,
                args.d_model,
                bias=True,
            )
        )

        self.norm_conv = nn.LayerNorm(args.d_model)
        self.conv = Convolution(args)

        self.norm_feed_forward2 = nn.LayerNorm(args.d_model)
        self.feed_forward2 = FeedForward(args.d_model, ff_hidden_dim, args.use_bias)

        self.norm_out = nn.LayerNorm(args.d_model)

    def set_attention_model(
        self,
        name: Literal["rel_pos", "rel_pos_local_attn", "normal"],
        context_size: Optional[tuple[int, int]] = (256, 256),
    ):
        new_attn = (
            RelPositionMultiHeadAttention(
                self.args.n_heads,
                self.args.d_model,
                bias=self.args.use_bias,
                pos_bias_u=self.args.pos_bias_u,
                pos_bias_v=self.args.pos_bias_v,
            )
            if name == "rel_pos"
            else RelPositionMultiHeadLocalAttention(
                self.args.n_heads,
                self.args.d_model,
                bias=self.args.use_bias,
                pos_bias_u=self.args.pos_bias_u,
                pos_bias_v=self.args.pos_bias_v,
                context_size=context_size if context_size is not None else (-1, -1),
            )
            if name == "rel_pos_local_attn"
            else MultiHeadAttention(
                self.args.n_heads,
                self.args.d_model,
                bias=True,
            )
        )

        new_attn.load_weights(tree_flatten(self.self_attn.parameters()))

        self.self_attn = new_attn

    def __call__(
        self,
        x: mx.array,
        pos_emb: mx.array | None = None,
        mask: mx.array | None = None,
        cache=None,
    ) -> mx.array:
        x += 0.5 * self.feed_forward1(self.norm_feed_forward1(x))

        x_norm = self.norm_self_att(x)
        x += self.self_attn(
            x_norm, x_norm, x_norm, mask=mask, pos_emb=pos_emb, cache=cache
        )

        x += self.conv(self.norm_conv(x), cache=cache)
        x += 0.5 * self.feed_forward2(self.norm_feed_forward2(x))

        return self.norm_out(x)


class DwStridingSubsampling(nn.Module):
    def __init__(self, args: ConformerArgs):
        super().__init__()

        assert (
            args.subsampling_factor > 0
            and (args.subsampling_factor & (args.subsampling_factor - 1)) == 0
        )
        self.subsampling_conv_chunking_factor = args.subsampling_conv_chunking_factor
        self._conv_channels = args.subsampling_conv_channels
        self._sampling_num = int(math.log(args.subsampling_factor, 2))
        self._stride = 2
        self._kernel_size = 3
        self._padding = (self._kernel_size - 1) // 2

        in_channels = 1
        final_freq_dim = args.feat_in
        for _ in range(self._sampling_num):
            final_freq_dim = (
                math.floor(
                    (final_freq_dim + 2 * self._padding - self._kernel_size)
                    / self._stride
                )
                + 1
            )
            if final_freq_dim < 1:
                raise ValueError("Non-positive final frequency dimension!")

        self.conv = [
            nn.Conv2d(
                in_channels=in_channels,
                out_channels=self._conv_channels,
                kernel_size=self._kernel_size,
                stride=self._stride,
                padding=self._padding,
            ),
            nn.ReLU(),
        ]
        in_channels = self._conv_channels

        for _ in range(self._sampling_num - 1):
            self.conv.append(
                nn.Conv2d(
                    in_channels=in_channels,
                    out_channels=in_channels,
                    kernel_size=self._kernel_size,
                    stride=self._stride,
                    padding=self._padding,
                    groups=in_channels,
                )
            )
            self.conv.append(
                nn.Conv2d(
                    in_channels=in_channels,
                    out_channels=self._conv_channels,
                    kernel_size=1,
                    stride=1,
                    padding=0,
                    groups=1,
                )
            )
            self.conv.append(nn.ReLU())

        self.out = nn.Linear(self._conv_channels * final_freq_dim, args.d_model)

    def conv_forward(self, x: mx.array) -> mx.array:
        x = x.transpose((0, 2, 3, 1))
        for layer in self.conv:
            x = layer(x)
        return x.transpose((0, 3, 1, 2))

    def conv_split_by_batch(self, x: mx.array) -> tuple[mx.array, bool]:
        b = x.shape[0]
        if b == 1:
            return x, False

        if self.subsampling_conv_chunking_factor > 1:
            cf = self.subsampling_conv_chunking_factor
        else:
            x_ceil = 2**31 / self._conv_channels * self._stride * self._stride
            p = math.ceil(math.log(x.size / x_ceil, 2))
            cf: int = 2**p

        new_batch_size = b // cf
        if new_batch_size == 0:
            return x, False

        return mx.concat(
            [self.conv_forward(chunk) for chunk in mx.split(x, new_batch_size, 0)]
        ), True

    def __call__(self, x: mx.array, lengths: mx.array) -> tuple[mx.array, mx.array]:
        for _ in range(self._sampling_num):
            lengths = (
                mx.floor(
                    (lengths + 2 * self._padding - self._kernel_size) / self._stride
                )
                + 1.0
            )
        lengths = lengths.astype(mx.int32)

        x = mx.expand_dims(x, axis=1)

        if self.subsampling_conv_chunking_factor != -1:
            if self.subsampling_conv_chunking_factor == 1:
                x_ceil = 2**31 / self._conv_channels * self._stride * self._stride
                need_to_split = x.size > x_ceil
            else:
                need_to_split = True

            if need_to_split:
                x, success = self.conv_split_by_batch(x)
                if not success:
                    # TODO: Add channel splitting
                    x = self.conv_forward(x)  # try anyways
            else:
                x = self.conv_forward(x)
        else:
            x = self.conv_forward(x)

        x = x.swapaxes(1, 2).reshape(x.shape[0], x.shape[2], -1)
        x = self.out(x)
        return x, lengths


class Conformer(nn.Module):
    def __init__(self, args: ConformerArgs):
        super().__init__()

        self.args = args

        if args.self_attention_model == "rel_pos":
            self.pos_enc = RelPositionalEncoding(
                d_model=args.d_model,
                max_len=args.pos_emb_max_len,
                scale_input=args.xscaling,
            )
        elif args.self_attention_model == "rel_pos_local_attn":
            self.pos_enc = LocalRelPositionalEncoding(
                d_model=args.d_model,
                max_len=args.pos_emb_max_len,
                scale_input=args.xscaling,
                context_size=(args.att_context_size[0], args.att_context_size[1])
                if args.att_context_size is not None
                else (-1, -1),
            )
        else:
            self.pos_enc = None

        if args.subsampling_factor > 1:
            if args.subsampling == "dw_striding" and args.causal_downsampling is False:
                self.pre_encode = DwStridingSubsampling(args)
            else:
                self.pre_encode = nn.Identity()
                raise NotImplementedError(
                    "Other subsampling haven't been implemented yet!"
                )
        else:
            self.pre_encode = nn.Linear(args.feat_in, args.d_model)

        self.layers = [ConformerBlock(args) for _ in range(args.n_layers)]

    def set_attention_model(
        self,
        name: Literal["rel_pos", "rel_pos_local_attn", "normal"],
        context_size: Optional[tuple[int, int]] = (256, 256),
    ):
        if name == "rel_pos":
            self.pos_enc = RelPositionalEncoding(
                d_model=self.args.d_model,
                max_len=self.args.pos_emb_max_len,
                scale_input=self.args.xscaling,
            )
        elif name == "rel_pos_local_attn":
            self.pos_enc = LocalRelPositionalEncoding(
                d_model=self.args.d_model,
                max_len=self.args.pos_emb_max_len,
                scale_input=self.args.xscaling,
                context_size=context_size if context_size else (-1, -1),
            )
        else:
            self.pos_enc = None

        for layer in self.layers:
            layer.set_attention_model(name, context_size)

    def __call__(
        self, x: mx.array, lengths: mx.array | None = None, cache=None
    ) -> tuple[mx.array, mx.array]:
        if lengths is None:
            lengths = mx.full(
                (x.shape[0],),
                x.shape[-2],
                dtype=mx.int64,
            )

        if isinstance(self.pre_encode, DwStridingSubsampling):
            x, out_lengths = self.pre_encode(x, lengths)
        elif isinstance(self.pre_encode, nn.Linear):
            x = self.pre_encode(x)
            out_lengths = lengths
        else:
            raise NotImplementedError("Non-implemented pre-encoding layer type!")

        if cache is None:
            cache = [None] * len(self.layers)

        pos_emb = None
        if self.pos_enc is not None:
            x, pos_emb = self.pos_enc(
                x,
                offset=cache[0].offset if cache[0] is not None else 0,  # type: ignore
            )

        for layer, c in zip(self.layers, cache):
            x = layer(x, pos_emb=pos_emb, cache=c)

        return x, out_lengths
````

## File: parakeet_mlx/attention.py
````python
import math

import mlx.core as mx
import mlx.nn as nn


class MultiHeadAttention(nn.Module):
    def __init__(
        self,
        n_head: int,
        n_feat: int,
        bias=True,
    ):
        super().__init__()

        self.n_head = n_head
        self.head_dim = n_feat // n_head
        self.scale = self.head_dim**-0.5

        self.linear_q = nn.Linear(n_feat, n_feat, bias=bias)
        self.linear_k = nn.Linear(n_feat, n_feat, bias=bias)
        self.linear_v = nn.Linear(n_feat, n_feat, bias=bias)
        self.linear_out = nn.Linear(n_feat, n_feat, bias=bias)

    def __call__(
        self,
        q: mx.array,
        k: mx.array,
        v: mx.array,
        pos_emb: mx.array | None = None,
        mask: mx.array | None = None,
        cache=None,
    ) -> mx.array:
        q, k, v = self.linear_q(q), self.linear_k(k), self.linear_v(v)

        batch, q_seq, _ = q.shape
        _, k_seq, _ = k.shape

        q = q.reshape(batch, q_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        k = k.reshape(batch, k_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        v = v.reshape(batch, k_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)

        if cache:
            k, v = cache.update_and_fetch_kv(k, v)

        o = mx.fast.scaled_dot_product_attention(q, k, v, scale=self.scale, mask=mask)
        o = o.transpose(0, 2, 1, 3).reshape(batch, q_seq, self.n_feat)

        return self.linear_out(o)


class RelPositionMultiHeadAttention(MultiHeadAttention):
    def __init__(
        self,
        n_head: int,
        n_feat: int,
        bias: bool = True,
        pos_bias_u: mx.array | None = None,
        pos_bias_v: mx.array | None = None,
    ):
        super().__init__(
            n_head=n_head,
            n_feat=n_feat,
            bias=bias,
        )

        self.linear_pos = nn.Linear(n_feat, n_feat, bias=False)

        if pos_bias_u is None:
            self._pos_bias_u_init = mx.zeros((self.n_head, self.head_dim))
        else:
            self._pos_bias_u_init = pos_bias_u

        if pos_bias_v is None:
            self._pos_bias_v_init = mx.zeros((self.n_head, self.head_dim))
        else:
            self._pos_bias_v_init = pos_bias_v

        self.pos_bias_u = self._pos_bias_u_init
        self.pos_bias_v = self._pos_bias_v_init

    def rel_shift(self, x: mx.array) -> mx.array:
        B, H, Tq, pos_len = x.shape
        padding = [(0, 0)] * (x.ndim - 1) + [(1, 0)]

        x = mx.pad(x, padding)
        x = x.reshape(B, H, pos_len + 1, Tq)
        x = x[:, :, 1:, :]
        x = x.reshape(B, H, Tq, pos_len)

        return x

    def __call__(
        self,
        q: mx.array,
        k: mx.array,
        v: mx.array,
        pos_emb: mx.array | None = None,
        mask: mx.array | None = None,
        cache=None,
    ) -> mx.array:
        if pos_emb is None:
            raise ValueError("pos_emb is necessary!")

        q, k, v = self.linear_q(q), self.linear_k(k), self.linear_v(v)

        p = self.linear_pos(pos_emb)  # p stands for position

        batch, q_seq, _ = q.shape
        _, k_seq, _ = k.shape
        _, pos_len, _ = p.shape

        q = q.reshape(batch, q_seq, self.n_head, self.head_dim)
        q_u = (q + self.pos_bias_u).transpose(0, 2, 1, 3)
        q_v = (q + self.pos_bias_v).transpose(0, 2, 1, 3)

        k = k.reshape(batch, k_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        v = v.reshape(batch, k_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        p = p.reshape(batch, pos_len, self.n_head, self.head_dim).transpose(0, 2, 1, 3)

        if cache is not None:
            k, v = cache.update_and_fetch_kv(k, v)

        matrix_bd = mx.matmul(q_v, p.swapaxes(-2, -1))
        matrix_bd = self.rel_shift(matrix_bd)
        matrix_bd = matrix_bd[:, :, :, : k.shape[-2]] * self.scale

        if mask is not None:
            mask = mx.expand_dims(mask, 0)
            matrix_bd[mask] = -mx.inf

        o = mx.fast.scaled_dot_product_attention(
            q_u, k, v, scale=self.scale, mask=matrix_bd
        )
        o = o.transpose(0, 2, 1, 3).reshape(batch, q_seq, -1)

        return self.linear_out(o)


class RelPositionMultiHeadLocalAttention(RelPositionMultiHeadAttention):
    def __init__(
        self,
        n_head: int,
        n_feat: int,
        bias: bool = True,
        pos_bias_u: mx.array | None = None,
        pos_bias_v: mx.array | None = None,
        context_size: tuple[int, int] = (256, 256),
    ):
        super().__init__(n_head, n_feat, bias, pos_bias_u, pos_bias_v)

        self.context_size = context_size

        if min(context_size) <= 0:
            raise ValueError(
                "Context size for RelPositionMultiHeadLocalAttention must be > 0."
            )

    def __call__(
        self,
        q: mx.array,
        k: mx.array,
        v: mx.array,
        pos_emb: mx.array | None = None,
        mask: mx.array | None = None,
        cache=None,
    ) -> mx.array:
        if pos_emb is None:
            raise ValueError("pos_emb is necessary!")

        if mask is None:
            mask = mx.zeros((q.shape[:2]), dtype=mx.bool_)  # type: ignore

        q, k, v = self.linear_q(q), self.linear_k(k), self.linear_v(v)
        p = self.linear_pos(pos_emb)  # p stands for position

        batch, q_seq, _ = q.shape
        _, k_seq, _ = k.shape
        _, pos_len, _ = p.shape

        q = q.reshape(batch, q_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        k = k.reshape(batch, k_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        v = v.reshape(batch, k_seq, self.n_head, self.head_dim).transpose(0, 2, 1, 3)
        p = p.reshape(batch, pos_len, self.n_head, self.head_dim).transpose(0, 2, 1, 3)

        if cache is not None:
            k, v = cache.update_and_fetch_kv(k, v)

        # pad to fit context size
        w = max(self.context_size)
        pad_len = (2 * w - q.shape[2] % (2 * w)) % (2 * w)

        q = mx.pad(q, ((0, 0), (0, 0), (0, pad_len), (0, 0)))
        k = mx.pad(k, ((0, 0), (0, 0), (0, pad_len), (0, 0)))
        v = mx.pad(v, ((0, 0), (0, 0), (0, pad_len), (0, 0)))
        mask = mx.pad(mask, ((0, 0), (0, pad_len)), constant_values=True)

        q_u = q + mx.expand_dims(self.pos_bias_u, 1)
        q_v = q + mx.expand_dims(self.pos_bias_v, 1)

        matrix_ac = self.matmul_qk(q_u, k, w)  # (batch, head, seq, 2w + 1)
        matrix_bd = mx.matmul(q_v, p.swapaxes(-2, -1))  # (batch, head, seq, 2w + 1)

        # we only add stuff in range and mask off unnecessaries
        matrix_ac[:, :, :, : self.context_size[0]] += matrix_bd[
            :, :, :, : self.context_size[0]
        ]
        matrix_ac[:, :, :, -(self.context_size[1] + 1) :] += matrix_bd[
            :, :, :, self.context_size[0] :
        ]
        matrix_ac[:, :, :, : (w - self.context_size[0])] = -mx.inf
        matrix_ac[:, :, :, (w + self.context_size[1] + 1) :] = -mx.inf

        scores = matrix_ac * self.scale

        mask = mx.expand_dims(mx.expand_dims(mask, 1), -1)
        float_mask = mx.where(mask, -mx.inf, 0.0).astype(matrix_ac.dtype)
        ones = mx.ones_like(float_mask)
        d_mask = self.matmul_qk(ones, float_mask, w)

        scores += d_mask

        attn = mx.softmax(scores, -1)
        attn = mx.where(mask, 0, attn)
        out = self.matmul_pv(attn, v, w)

        out = out.reshape(batch, -1, self.n_head * self.head_dim)[:, :q_seq]

        return self.linear_out(out)

    def matmul_qk(self, q: mx.array, k: mx.array, w: int) -> mx.array:
        KERNEL = """
        // D, W are provided as constant
        uint B = q_shape[0];
        uint H = q_shape[1];
        uint S_q = q_shape[2];
        uint S_k = k_shape[2];
        uint K_rel = 2 * W + 1;

        uint target_idx = thread_position_in_grid.x;
        uint k_rel_idx = thread_position_in_grid.y;

        if (target_idx >= B * H * S_q) return;

        uint s_q_idx = target_idx % S_q;
        uint remaining_idx = target_idx / S_q;
        uint h_idx = remaining_idx % H;
        uint b_idx = remaining_idx / H;
        uint k_offset = k_rel_idx;

        uint stick_q_k_idx = S_k - S_q + s_q_idx;
        // stick to right (assuming S_k >= S_q)

        int s_k_idx_signed = int(stick_q_k_idx) + int(k_offset) - int(W);
        bool is_out_of_bounds = (s_k_idx_signed < 0) || (s_k_idx_signed >= S_k);

        T result;

        if (!is_out_of_bounds) {
            uint s_k_idx = uint(s_k_idx_signed);

            // q[b, h, s_q, d]
            uint Q_D_stride = D;
            uint Q_S_stride = S_q * Q_D_stride;
            uint Q_H_stride = H * Q_S_stride;
            // k[b, h, s_k, d]
            uint K_D_stride = D;
            uint K_S_stride = S_k * K_D_stride;
            uint K_H_stride = H * K_S_stride;

            uint q_base_offset =
                b_idx * Q_H_stride + h_idx * Q_S_stride + s_q_idx * Q_D_stride;
            uint k_base_offset =
                b_idx * K_H_stride + h_idx * K_S_stride + s_k_idx * K_D_stride;

            const device T* q_vec_ptr = q + q_base_offset;
            const device T* k_vec_ptr = k + k_base_offset;

            result = T(0.0);
            uint d_idx = 0;

            // hand unrolling
            for (; d_idx + 16 <= D; d_idx += 16) {
                T q_vals[16], k_vals[16];

                for (uint i = 0; i < 16; ++i) {
                    q_vals[i] = q_vec_ptr[d_idx + i];
                    k_vals[i] = k_vec_ptr[d_idx + i];
                }

                result +=
                    q_vals[0] * k_vals[0] + q_vals[1] * k_vals[1] +
                    q_vals[2] * k_vals[2] + q_vals[3] * k_vals[3] +
                    q_vals[4] * k_vals[4] + q_vals[5] * k_vals[5] +
                    q_vals[6] * k_vals[6] + q_vals[7] * k_vals[7] +
                    q_vals[8] * k_vals[8] + q_vals[9] * k_vals[9] +
                    q_vals[10] * k_vals[10] + q_vals[11] * k_vals[11] +
                    q_vals[12] * k_vals[12] + q_vals[13] * k_vals[13] +
                    q_vals[14] * k_vals[14] + q_vals[15] * k_vals[15];
            }

            for (; d_idx + 8 <= D; d_idx += 8) {
                result +=
                    q_vec_ptr[d_idx] * k_vec_ptr[d_idx] +
                    q_vec_ptr[d_idx + 1] * k_vec_ptr[d_idx + 1] +
                    q_vec_ptr[d_idx + 2] * k_vec_ptr[d_idx + 2] +
                    q_vec_ptr[d_idx + 3] * k_vec_ptr[d_idx + 3] +
                    q_vec_ptr[d_idx + 4] * k_vec_ptr[d_idx + 4] +
                    q_vec_ptr[d_idx + 5] * k_vec_ptr[d_idx + 5] +
                    q_vec_ptr[d_idx + 6] * k_vec_ptr[d_idx + 6] +
                    q_vec_ptr[d_idx + 7] * k_vec_ptr[d_idx + 7];
            }

            for (; d_idx + 4 <= D; d_idx += 4) {
                result +=
                    q_vec_ptr[d_idx] * k_vec_ptr[d_idx] +
                    q_vec_ptr[d_idx + 1] * k_vec_ptr[d_idx + 1] +
                    q_vec_ptr[d_idx + 2] * k_vec_ptr[d_idx + 2] +
                    q_vec_ptr[d_idx + 3] * k_vec_ptr[d_idx + 3];
            }

            for (; d_idx < D; ++d_idx) {
                result += q_vec_ptr[d_idx] * k_vec_ptr[d_idx];
            }
        } else {
            result = T(-INFINITY);
        }

        uint out_idx = target_idx * K_rel + k_rel_idx;
        out[out_idx] = result;
        """

        B, H, S_q, D = q.shape
        _, _, S_k, _ = k.shape

        output_shape = (B, H, S_q, 2 * w + 1)

        grid_dim_x = B * H * S_q
        grid_dim_y = 2 * w + 1
        grid_dim_z = 1

        kernel_fn = mx.fast.metal_kernel(
            name="local_qk_perf",
            input_names=["q", "k"],
            output_names=["out"],
            source=KERNEL,
        )

        grid_dim_x = max(1, grid_dim_x)
        grid_dim_y = max(1, grid_dim_y)

        if D >= 256:
            tg_y = min(grid_dim_y, 4)
            tg_x = min(grid_dim_x, 256)
        elif D >= 128:
            tg_y = min(grid_dim_y, 8)
            tg_x = min(grid_dim_x, 128)
        elif D >= 32:
            tg_y = min(grid_dim_y, 16)
            tg_x = min(grid_dim_x, 64)
        else:
            tg_y = min(grid_dim_y, 32)
            tg_x = min(grid_dim_x, 32)

        if tg_x > 32:
            tg_x = 64
        elif tg_x > 16:
            tg_x = 32
        elif tg_x > 8:
            tg_x = 16
        elif tg_x > 4:
            tg_x = 8
        else:
            tg_x = max(tg_x, 1)

        tg_x = max(tg_x, 1)
        tg_y = max(tg_y, 1)

        outputs = kernel_fn(  # type: ignore
            inputs=[q, k],
            template=[
                ("T", q.dtype),
                ("W", w),
                ("D", D),
            ],
            grid=(grid_dim_x, grid_dim_y, grid_dim_z),
            threadgroup=(tg_x, tg_y, 1),
            output_shapes=[output_shape],
            output_dtypes=[q.dtype],
        )
        return outputs[0]

    def matmul_pv(self, prob: mx.array, v: mx.array, w: int) -> mx.array:
        KERNEL = """
        // D, W, D_v are provided as constant
        uint B = prob_shape[0];
        uint H = prob_shape[1];
        uint S_p = prob_shape[2];
        uint S_v = v_shape[2];
        uint K_rel = 2 * W + 1;

        uint d_idx = thread_position_in_grid.x;
        uint s_p_idx = thread_position_in_grid.y;
        uint bh_idx = thread_position_in_grid.z;  // merged

        if (d_idx >= D_v || s_p_idx >= S_p || bh_idx >= (B * H)) {
            return;
        }

        uint b_idx = bh_idx / H;
        uint h_idx = bh_idx % H;

        T current_sum = 0.0f;

        // p[b, h, s_p, k_rel]
        uint P_H_stride = S_p * K_rel;
        uint P_B_stride = H * P_H_stride;

        // v[b, h, s_v, d]
        uint V_H_stride = S_v * D_v;
        uint V_B_stride = H * V_H_stride;

        // out[b, s_p, h, d]
        uint O_S_stride = D_v * H;
        uint O_B_stride = S_p * O_S_stride;

        uint stick_p_v_idx = S_v - S_p + s_p_idx;
        // stick to right (assuming S_v >= S_p)

        uint k = 0;
        // hand unrolling
        for (; k + 16 <= K_rel; k += 16) {
            float prob_vals[16], v_vals[16];
            int s_v_indices[16];
            bool valid[16];

            for (uint i = 0; i < 16; ++i) {
                s_v_indices[i] = int(stick_p_v_idx) + int(k + i) - int(W);
                valid[i] = (s_v_indices[i] >= 0 && s_v_indices[i] < S_v);
                if (valid[i]) {
                    uint prob_idx = b_idx * P_B_stride + h_idx * P_H_stride + s_p_idx * K_rel + (k + i);
                    uint v_idx = b_idx * V_B_stride + h_idx * V_H_stride + uint(s_v_indices[i]) * D_v + d_idx;
                    prob_vals[i] = prob[prob_idx];
                    v_vals[i] = v[v_idx];
                } else {
                    prob_vals[i] = 0.0f;
                    v_vals[i] = 0.0f;
                }
            }

            current_sum +=
                prob_vals[0] * v_vals[0] + prob_vals[1] * v_vals[1] +
                prob_vals[2] * v_vals[2] + prob_vals[3] * v_vals[3] +
                prob_vals[4] * v_vals[4] + prob_vals[5] * v_vals[5] +
                prob_vals[6] * v_vals[6] + prob_vals[7] * v_vals[7] +
                prob_vals[8] * v_vals[8] + prob_vals[9] * v_vals[9] +
                prob_vals[10] * v_vals[10] + prob_vals[11] * v_vals[11] +
                prob_vals[12] * v_vals[12] + prob_vals[13] * v_vals[13] +
                prob_vals[14] * v_vals[14] + prob_vals[15] * v_vals[15];
        }

        for (; k + 8 <= K_rel; k += 8) {
            for (uint i = 0; i < 8; ++i) {
                int s_v_idx_signed = int(stick_p_v_idx) + int(k + i) - int(W);
                if (s_v_idx_signed >= 0 && s_v_idx_signed < S_v) {
                    uint s_v_idx = uint(s_v_idx_signed);
                    uint prob_idx = b_idx * P_B_stride + h_idx * P_H_stride + s_p_idx * K_rel + (k + i);
                    uint v_idx = b_idx * V_B_stride + h_idx * V_H_stride + s_v_idx * D_v + d_idx;
                    current_sum += prob[prob_idx] * v[v_idx];
                }
            }
        }

        for (; k + 4 <= K_rel; k += 4) {
            for (uint i = 0; i < 4; ++i) {
                int s_v_idx_signed = int(stick_p_v_idx) + int(k + i) - int(W);
                if (s_v_idx_signed >= 0 && s_v_idx_signed < S_v) {
                    uint s_v_idx = uint(s_v_idx_signed);
                    uint prob_idx = b_idx * P_B_stride + h_idx * P_H_stride + s_p_idx * K_rel + (k + i);
                    uint v_idx = b_idx * V_B_stride + h_idx * V_H_stride + s_v_idx * D_v + d_idx;
                    current_sum += prob[prob_idx] * v[v_idx];
                }
            }
        }

        for (; k < K_rel; ++k) {
            int s_v_idx_signed = int(stick_p_v_idx) + int(k) - int(W);
            if (s_v_idx_signed >= 0 && s_v_idx_signed < S_v) {
                uint s_v_idx = uint(s_v_idx_signed);
                uint prob_idx = b_idx * P_B_stride + h_idx * P_H_stride + s_p_idx * K_rel + k;
                uint v_idx = b_idx * V_B_stride + h_idx * V_H_stride + s_v_idx * D_v + d_idx;
                current_sum += prob[prob_idx] * v[v_idx];
            }
        }

        uint out_idx =
            b_idx * O_B_stride + s_p_idx * O_S_stride + h_idx * D_v + d_idx;

        context_out[out_idx] = current_sum;
        """

        B, H, S_p, K_rel = prob.shape
        _, _, S_v, D_v = v.shape

        kernel_fn = mx.fast.metal_kernel(
            name="local_pv_matmul",
            input_names=["prob", "v"],
            output_names=["context_out"],
            source=KERNEL,
        )

        output_shape = (B, S_p, H, D_v)

        grid_dim_x = D_v
        grid_dim_y = S_p
        grid_dim_z = B * H

        tg_x = min(grid_dim_x, 32)
        tg_y = min(grid_dim_y, 1024 // tg_x)
        tg_x = max(tg_x, 1)
        tg_y = max(tg_y, 1)

        outputs = kernel_fn(  # type: ignore
            inputs=[prob, v],
            template=[("T", prob.dtype), ("W", w), ("D", K_rel), ("D_v", D_v)],
            grid=(grid_dim_x, grid_dim_y, grid_dim_z),
            threadgroup=(tg_x, tg_y, 1),
            output_shapes=[output_shape],
            output_dtypes=[prob.dtype],
        )

        return outputs[0]


class RelPositionalEncoding(nn.Module):
    def __init__(
        self,
        d_model: int,
        max_len: int = 5000,
        scale_input: bool = True,
    ):
        assert d_model % 2 == 0 and max_len > 0
        super().__init__()

        self.d_model = d_model
        self.max_len = max_len
        self.scale = math.sqrt(self.d_model) if scale_input else 1.0
        self.calculate_pe()

    def calculate_pe(self):
        positions = mx.arange(self.max_len - 1, -self.max_len, -1, dtype=mx.int32)
        positions = mx.expand_dims(positions, axis=1).astype(mx.float32)

        div_term = mx.exp(
            mx.arange(0, self.d_model, 2, dtype=mx.float32)
            * -(math.log(10000.0) / self.d_model)
        )
        pe = mx.zeros((2 * self.max_len - 1, self.d_model), dtype=mx.float32)

        pe[:, 0::2] = mx.sin(positions * div_term)
        pe[:, 1::2] = mx.cos(positions * div_term)

        self._pe = mx.expand_dims(pe, axis=0).astype(mx.float32)

        mx.eval(self._pe)

    def __call__(self, x: mx.array, offset: int = 0) -> tuple[mx.array, mx.array]:
        input_len = x.shape[1] + offset

        if input_len > self.max_len:
            self.max_len = input_len + 1
            self.calculate_pe()

        x = x * self.scale

        buffer_len = self._pe.shape[1]
        start_idx = buffer_len // 2 - (input_len - 1)
        end_idx = buffer_len // 2 + (input_len - 1) + 1

        pos_emb = self._pe[:, start_idx:end_idx].astype(x.dtype)

        return x, pos_emb


class LocalRelPositionalEncoding(RelPositionalEncoding):
    def __init__(
        self,
        d_model: int,
        max_len: int = 5000,
        scale_input: bool = True,
        context_size: tuple[int, int] = (256, 256),
    ):
        self.left_context, self.right_context = context_size

        super().__init__(d_model, max_len, scale_input)

    def calculate_pe(self):
        positions = mx.arange(
            self.left_context, -self.right_context - 1, -1, dtype=mx.int32
        )
        positions = mx.expand_dims(positions, axis=1).astype(mx.float32)

        div_term = mx.exp(
            mx.arange(0, self.d_model, 2, dtype=mx.float32)
            * -(math.log(10000.0) / self.d_model)
        )
        pe = mx.zeros(
            (self.left_context + self.right_context + 1, self.d_model), dtype=mx.float32
        )

        pe[:, 0::2] = mx.sin(positions * div_term)
        pe[:, 1::2] = mx.cos(positions * div_term)

        self._pe = mx.expand_dims(pe, axis=0).astype(mx.float32)

        mx.eval(self._pe)

    def __call__(self, x: mx.array, offset: int = 0) -> tuple[mx.array, mx.array]:
        x = x * self.scale

        end_idx = self.left_context + self.right_context + 1
        pos_emb = self._pe[:, :end_idx].astype(x.dtype)

        return x, pos_emb
````

## File: parakeet_mlx/audio.py
````python
import functools
import shutil
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError, run

import librosa
import mlx.core as mx
import numpy as np


@dataclass
class PreprocessArgs:
    sample_rate: int
    normalize: str
    window_size: float
    window_stride: float
    window: str
    features: int
    n_fft: int
    dither: float
    pad_to: int = 0
    pad_value: float = 0
    preemph: float | None = 0.97
    mag_power: float = 2.0

    @property
    def win_length(self) -> int:
        return int(self.window_size * self.sample_rate)

    @property
    def hop_length(self) -> int:
        return int(self.window_stride * self.sample_rate)

    def __post_init__(self):
        # only slow at first run, should be acceptable to most of users
        self._filterbanks = mx.array(
            librosa.filters.mel(
                sr=self.sample_rate,
                n_fft=self.n_fft,
                n_mels=self.features,
                fmin=0,
                fmax=self.sample_rate / 2,
                norm="slaney",
            ),
            dtype=mx.float32,
        )


# thanks to mlx-whisper too!
def load_audio(
    filename: Path, sampling_rate: int, dtype: mx.Dtype = mx.bfloat16
) -> mx.array:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg is not installed or not in your PATH.")

    cmd = ["ffmpeg", "-nostdin", "-i", str(filename)]

    # fmt: off
    cmd.extend(
        [
            "-threads", "0",
            "-f", "s16le",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            "-ar", str(sampling_rate),
            "-",
        ]
    )
    # fmt: on
    try:
        out = run(cmd, capture_output=True, check=True).stdout
    except CalledProcessError as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return mx.array(np.frombuffer(out, np.int16).flatten()).astype(mx.float32) / 32768.0


# thanks to https://github.com/ml-explore/mlx-examples/blob/main/whisper/mlx_whisper/audio.py
@functools.lru_cache(None)
def hanning(size):
    return mx.array(np.hanning(size + 1)[:-1])


@functools.lru_cache(None)
def hamming(size):
    return mx.array(np.hamming(size + 1)[:-1])


@functools.lru_cache(None)
def blackman(size):
    return mx.array(np.blackman(size + 1)[:-1])


@functools.lru_cache(None)
def bartlett(size):
    return mx.array(np.bartlett(size + 1)[:-1])


def stft(
    x, n_fft, hop_length=None, win_length=None, window=None, axis=-1, pad_mode="reflect"
):
    if win_length is None:
        win_length = n_fft
    if hop_length is None:
        hop_length = n_fft // 4
    if window is None:
        window = mx.ones(win_length)

    if win_length != n_fft:
        if win_length > n_fft:
            window = window[:n_fft]
        else:
            padding = [(0, n_fft - win_length)]
            window = mx.pad(window, padding)

    def _pad(x, padding, pad_mode="constant"):
        if pad_mode == "constant":
            return mx.pad(x, [(padding, padding)])
        elif pad_mode == "reflect":
            prefix = x[1 : padding + 1][::-1]
            suffix = x[-(padding + 1) : -1][::-1]
            return mx.concatenate([prefix, x, suffix])
        else:
            raise ValueError(f"Invalid pad_mode {pad_mode}")

    padding = n_fft // 2
    x = _pad(x, padding, pad_mode)

    strides = [hop_length, 1]
    t = (x.size - win_length + hop_length) // hop_length
    shape = [t, n_fft]
    x = mx.as_strided(x, shape=shape, strides=strides)
    return mx.fft.rfft(x * window)


def get_logmel(x: mx.array, args: PreprocessArgs) -> mx.array:
    original_dtype = x.dtype

    if args.pad_to > 0:
        if x.shape[-1] < args.pad_to:
            pad_length = args.pad_to - x.shape[-1]
            x = mx.pad(x, ((0, pad_length),), constant_values=args.pad_value)

    if args.preemph is not None:
        x = mx.concat([x[:1], x[1:] - args.preemph * x[:-1]], axis=0)

    window = (
        hanning(args.win_length).astype(x.dtype)
        if args.window == "hanning"
        else hamming(args.win_length).astype(x.dtype)
        if args.window == "hamming"
        else blackman(args.win_length).astype(x.dtype)
        if args.window == "blackman"
        else bartlett(args.win_length).astype(x.dtype)
        if args.window == "bartlett"
        else None
    )
    x = stft(x, args.n_fft, args.hop_length, args.win_length, window)
    abs = mx.abs(mx.view(x, original_dtype))
    x = abs[..., ::2] + abs[..., 1::2]

    if args.mag_power != 1.0:
        x = mx.power(x, args.mag_power)

    x = mx.matmul(args._filterbanks.astype(x.dtype), x.T)
    x = mx.log(x + 1e-5)

    if args.normalize == "per_feature":
        mean = mx.mean(x, axis=1, keepdims=True)
        std = mx.std(x, axis=1, keepdims=True)
        normalized_mel = (x - mean) / (std + 1e-5)
    else:
        mean = mx.mean(x)
        std = mx.std(x)
        normalized_mel = (x - mean) / (std + 1e-5)

    normalized_mel = normalized_mel.T
    normalized_mel = mx.expand_dims(normalized_mel, axis=0)

    return normalized_mel.astype(original_dtype)
````

## File: pyproject.toml
````toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "parakeet-mlx"
version = "0.3.1"
description = "An implementation of the Nvidia's Parakeet models for Apple Silicon using MLX."
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "dacite>=1.9.2",
    "huggingface-hub>=0.30.2",
    "librosa>=0.11.0",
    "mlx>=0.22.1",
    "numpy>=2.2.5",
    "typer>=0.15.3",
]
license = "Apache-2.0"
keywords = [
    "mlx",
    "parakeet",
    "asr",
    "nvidia",
    "apple",
    "speech",
    "recognition",
    "ml",
]

[project.urls]
Repository = "https://github.com/senstella/parakeet-mlx.git"
Issues = "https://github.com/senstella/parakeet-mlx/issues"

[project.scripts]
parakeet-mlx = "parakeet_mlx.cli:app"
````

## File: README.md
````markdown
# Parakeet MLX

An implementation of the Parakeet models - Nvidia's ASR(Automatic Speech Recognition) models - for Apple Silicon using MLX.

## Installation

> [!NOTE]
> Make sure you have `ffmpeg` installed on your system first, otherwise CLI won't work properly.

Using [uv](https://docs.astral.sh/uv/) - recommended way:

```bash
uv add parakeet-mlx -U
```

Or, for the CLI:

```bash
uv tool install parakeet-mlx -U
```

Using pip:

```bash
pip install parakeet-mlx -U
```

## CLI Quick Start

```bash
parakeet-mlx <audio_files> [OPTIONS]
```

## Arguments

- `audio_files`: One or more audio files to transcribe (WAV, MP3, etc.)

## Options

- `--model` (default: `mlx-community/parakeet-tdt-0.6b-v2`)
  - Hugging Face repository of the model to use

- `--output-dir` (default: current directory)
  - Directory to save transcription outputs

- `--output-format` (default: srt)
  - Output format (txt/srt/vtt/json/all)

- `--output-template` (default: `{filename}`)
  - Template for output filenames, `{filename}`, `{index}`, `{date}` is supported.

- `--highlight-words` (default: False)
  - Enable word-level timestamps in SRT/VTT outputs

- `--verbose` / `-v` (default: False)
  - Print detailed progress information

- `--chunk-duration` (default: 120 seconds)
  - Chunking duration in seconds for long audio, `0` to disable chunking

- `--overlap-duration` (default: 15 seconds)
  - Overlap duration in seconds if using chunking

- `--fp32` / `--bf16` (default: `bf16`)
  - Determine the precision to use

## Examples

```bash
# Basic transcription
parakeet-mlx audio.mp3

# Multiple files with word-level timestamps of VTT subtitle
parakeet-mlx *.mp3 --output-format vtt --highlight-words

# Generate all output formats
parakeet-mlx audio.mp3 --output-format all
```


## Python API Quick Start

Transcribe a file:

```py
from parakeet_mlx import from_pretrained

model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v2")

result = model.transcribe("audio_file.wav")

print(result.text)
```

Check timestamps:

```py
from parakeet_mlx import from_pretrained

model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v2")

result = model.transcribe("audio_file.wav")

print(result.sentences)
# [AlignedSentence(text="Hello World.", start=1.01, end=2.04, duration=1.03, tokens=[...])]
```

Do chunking:

```py
from parakeet_mlx import from_pretrained

model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v2")

result = model.transcribe("audio_file.wav", chunk_duration=60 * 2.0, overlap_duration=15.0)

print(result.sentences)
```

## Timestamp Result

- `AlignedResult`: Top-level result containing the full text and sentences
  - `text`: Full transcribed text
  - `sentences`: List of `AlignedSentence`
- `AlignedSentence`: Sentence-level alignments with start/end times
  - `text`: Sentence text
  - `start`: Start time in seconds
  - `end`: End time in seconds
  - `duration`: Between `start` and `end`.
  - `tokens`: List of `AlignedToken`
- `AlignedToken`: Word/token-level alignments with precise timestamps
  - `text`: Token text
  - `start`: Start time in seconds
  - `end`: End time in seconds
  - `duration`: Between `start` and `end`.

## Streaming Transcription

For real-time transcription, use the `transcribe_stream` method which creates a streaming context:

```py
from parakeet_mlx import from_pretrained
from parakeet_mlx.audio import load_audio
import numpy as np

model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v2")

# Create a streaming context
with model.transcribe_stream(
    context_size=(256, 256),  # (left_context, right_context) frames
) as transcriber:
    # Simulate real-time audio chunks
    audio_data = load_audio("audio_file.wav", model.preprocessor_config.sample_rate)
    chunk_size = model.preprocessor_config.sample_rate  # 1 second chunks

    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i+chunk_size]
        transcriber.add_audio(chunk)

        # Access current transcription
        result = transcriber.result
        print(f"Current text: {result.text}")

        # Access finalized and draft tokens
        # transcriber.finalized_tokens
        # transcriber.draft_tokens
```

### Streaming Parameters

- `context_size`: Tuple of (left_context, right_context) for attention windows
  - Controls how many frames the model looks at before and after current position
  - Default: (256, 256)

- `depth`: Number of encoder layers that preserve exact computation across chunks
  - Controls how many layers maintain exact equivalence with non-streaming forward pass
  - depth=1: Only first encoder layer matches non-streaming computation exactly
  - depth=2: First two layers match exactly, and so on
  - depth=N (total layers): Full equivalence to non-streaming forward pass
  - Higher depth means more computational consistency with non-streaming mode
  - Default: 1

- `keep_original_attention`: Whether to keep original attention mechanism
  - False: Switches to local attention for streaming (recommended)
  - True: Keeps original attention (less suitable for streaming)
  - Default: False

## Low-Level API

To transcribe log-mel spectrum directly, you can do the following:

```python
import mlx.core as mx
from parakeet_mlx.audio import get_logmel, load_audio

# Load and preprocess audio manually
audio = load_audio("audio.wav", model.preprocessor_config.sample_rate)
mel = get_logmel(audio, model.preprocessor_config)

# Generate transcription with alignments
# Accepts both [batch, sequence, feat] and [sequence, feat]
# `alignments` is list of AlignedResult. (no matter if you fed batch dimension or not!)
alignments = model.generate(mel)
```

## Todo

- [X] Add CLI for better usability
- [X] Add support for other Parakeet variants
- [X] Streaming input (real-time transcription with `transcribe_stream`)
- [ ] Option to enhance chosen words' accuracy
- [ ] Chunking with continuous context (partially achieved with streaming)


## Acknowledgments

- Thanks to [Nvidia](https://www.nvidia.com/) for training these awesome models and writing cool papers and providing nice implementation.
- Thanks to [MLX](https://github.com/ml-explore/mlx) project for providing the framework that made this implementation possible.
- Thanks to [audiofile](https://github.com/audeering/audiofile) and [audresample](https://github.com/audeering/audresample), [numpy](https://numpy.org), [librosa](https://librosa.org) for audio processing.
- Thanks to [dacite](https://github.com/konradhalas/dacite) for config management.

## License

Apache 2.0
````

## File: parakeet_mlx/parakeet.py
````python
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

import mlx.core as mx
import mlx.nn as nn

from parakeet_mlx import tokenizer
from parakeet_mlx.alignment import (
    AlignedResult,
    AlignedToken,
    merge_longest_common_subsequence,
    merge_longest_contiguous,
    sentences_to_result,
    tokens_to_sentences,
)
from parakeet_mlx.audio import PreprocessArgs, get_logmel, load_audio
from parakeet_mlx.cache import ConformerCache, RotatingConformerCache
from parakeet_mlx.conformer import Conformer, ConformerArgs
from parakeet_mlx.ctc import AuxCTCArgs, ConvASRDecoder, ConvASRDecoderArgs
from parakeet_mlx.rnnt import JointArgs, JointNetwork, PredictArgs, PredictNetwork


@dataclass
class TDTDecodingArgs:
    model_type: str
    durations: list[int]
    greedy: dict | None


@dataclass
class RNNTDecodingArgs:
    greedy: dict | None


@dataclass
class CTCDecodingArgs:
    greedy: dict | None


@dataclass
class ParakeetTDTArgs:
    preprocessor: PreprocessArgs
    encoder: ConformerArgs
    decoder: PredictArgs
    joint: JointArgs
    decoding: TDTDecodingArgs


@dataclass
class ParakeetRNNTArgs:
    preprocessor: PreprocessArgs
    encoder: ConformerArgs
    decoder: PredictArgs
    joint: JointArgs
    decoding: RNNTDecodingArgs


@dataclass
class ParakeetCTCArgs:
    preprocessor: PreprocessArgs
    encoder: ConformerArgs
    decoder: ConvASRDecoderArgs
    decoding: CTCDecodingArgs


@dataclass
class ParakeetTDTCTCArgs(ParakeetTDTArgs):
    aux_ctc: AuxCTCArgs


# API
@dataclass
class DecodingConfig:
    decoding: str = "greedy"


# common methods
class BaseParakeet(nn.Module):
    """Base parakeet model for interface purpose"""

    def __init__(self, preprocess_args: PreprocessArgs, encoder_args: ConformerArgs):
        super().__init__()

        self.preprocessor_config = preprocess_args
        self.encoder_config = encoder_args

        self.encoder = Conformer(encoder_args)

    def generate(
        self, mel: mx.array, *, decoding_config: DecodingConfig = DecodingConfig()
    ) -> list[AlignedResult]:
        """
        Generate transcription results from the Parakeet model, handling batches and single input.
        Args:
            mel (mx.array):
                Mel-spectrogram input with shape [batch, sequence, mel_dim] for
                batch processing or [sequence, mel_dim] for single input.
            decoding_config (DecodingConfig, optional):
                Configuration object that controls decoding behavior and
                parameters for the generation process. Defaults to DecodingConfig().
        Returns:
            list[AlignedResult]: List of transcription results with aligned tokens
                and sentences, one for each input in the batch.
        """
        raise NotImplementedError

    def transcribe(
        self,
        path: Path | str,
        *,
        dtype: mx.Dtype = mx.bfloat16,
        chunk_duration: Optional[float] = None,
        overlap_duration: float = 15.0,
        chunk_callback: Optional[Callable] = None,
    ) -> AlignedResult:
        """
        Transcribe an audio file, with optional chunking for long files.
        Args:
            path (Path | str):
                Path to the audio file to be transcribed.
            dtype (mx.Dtype, optional):
                Data type for processing the audio. Defaults to mx.bfloat16.
            chunk_duration (float, optional):
                If provided, splits audio into chunks of this length (in seconds)
                for processing. When None, processes the entire file at once.
                Defaults to None.
            overlap_duration (float, optional):
                Overlap between consecutive chunks in seconds. Only used when
                chunk_duration is specified. Defaults to 15.0.
            chunk_callback (Callable, optional):
                A function to call when each chunk is processed. The callback
                is called with (current_position, total_position) arguments
                to track progress. Defaults to None.
        Returns:
            AlignedResult: Transcription result with aligned tokens and sentences.
        """
        audio_path = Path(path)
        audio_data = load_audio(audio_path, self.preprocessor_config.sample_rate, dtype)

        if chunk_duration is None:
            mel = get_logmel(audio_data, self.preprocessor_config)
            return self.generate(mel)[0]

        audio_length_seconds = len(audio_data) / self.preprocessor_config.sample_rate

        if audio_length_seconds <= chunk_duration:
            mel = get_logmel(audio_data, self.preprocessor_config)
            return self.generate(mel)[0]

        chunk_samples = int(chunk_duration * self.preprocessor_config.sample_rate)
        overlap_samples = int(overlap_duration * self.preprocessor_config.sample_rate)

        all_tokens = []

        for start in range(0, len(audio_data), chunk_samples - overlap_samples):
            end = min(start + chunk_samples, len(audio_data))

            if chunk_callback is not None:
                chunk_callback(end, len(audio_data))

            if end - start < self.preprocessor_config.hop_length:
                break  # prevent zero-length log mel

            chunk_audio = audio_data[start:end]
            chunk_mel = get_logmel(chunk_audio, self.preprocessor_config)

            chunk_result = self.generate(chunk_mel)[0]

            chunk_offset = start / self.preprocessor_config.sample_rate
            for sentence in chunk_result.sentences:
                for token in sentence.tokens:
                    token.start += chunk_offset
                    token.end = token.start + token.duration

            if all_tokens:
                try:
                    all_tokens = merge_longest_contiguous(
                        all_tokens,
                        chunk_result.tokens,
                        overlap_duration=overlap_duration,
                    )
                except RuntimeError:
                    all_tokens = merge_longest_common_subsequence(
                        all_tokens,
                        chunk_result.tokens,
                        overlap_duration=overlap_duration,
                    )
            else:
                all_tokens = chunk_result.tokens

        result = sentences_to_result(tokens_to_sentences(all_tokens))
        return result

    def transcribe_stream(
        self,
        context_size: tuple[int, int] = (256, 256),
        depth=1,
        *,
        keep_original_attention: bool = False,
        decoding_config: DecodingConfig = DecodingConfig(),
    ) -> "StreamingParakeet":
        """
        Create a StreamingParakeet object for real-time (streaming) inference.
        Args:
            context_size (tuple[int, int], optional):
                A pair (left_context, right_context) for attention context windows.
            depth (int, optional):
                How many encoder layers will carry over their key/value
                cache (i.e. hidden state) exactly across chunks. Because
                we use local (non-causal) attention, the cache is only
                guaranteed to match a full forward pass up through each
                cached layer:
                    • depth=1 (default): only the first encoder layer's
                    cache matches exactly.
                    • depth=2: the first two layers match, and so on.
                    • depth=N (model's total layers): full equivalence to
                    a non-streaming forward pass.
                Setting `depth` larger than the model's total number
                of encoder layers won't have any impacts.
            keep_original_attention (bool, optional):
                Whether to preserve the original attention class
                during streaming inference. Defaults to False. (Will switch to local attention.)
            decoding_config (DecodingConfig, optional):
                Configuration object that controls decoding behavior
                Defaults to DecodingConfig().
        Returns:
            StreamingParakeet: A context manager for streaming inference.
        """
        return StreamingParakeet(
            self,
            context_size,
            depth,
            decoding_config=decoding_config,
            keep_original_attention=keep_original_attention,
        )


# models
class ParakeetTDT(BaseParakeet):
    """MLX Implementation of Parakeet-TDT Model"""

    def __init__(self, args: ParakeetTDTArgs):
        super().__init__(args.preprocessor, args.encoder)

        assert args.decoding.model_type == "tdt", "Model must be a TDT model"

        self.vocabulary = args.joint.vocabulary
        self.durations = args.decoding.durations
        self.max_symbols: int | None = (
            args.decoding.greedy.get("max_symbols", None)
            if args.decoding.greedy
            else None
        )

        self.decoder = PredictNetwork(args.decoder)
        self.joint = JointNetwork(args.joint)

    def decode(
        self,
        features: mx.array,
        lengths: Optional[mx.array] = None,
        last_token: Optional[list[Optional[int]]] = None,
        hidden_state: Optional[list[Optional[tuple[mx.array, mx.array]]]] = None,
        *,
        config: DecodingConfig = DecodingConfig(),
    ) -> tuple[list[list[AlignedToken]], list[Optional[tuple[mx.array, mx.array]]]]:
        """Run TDT decoder with features, optional length and decoder state. Outputs list[list[AlignedToken]] and updated hidden state"""
        assert config.decoding == "greedy", (
            "Only greedy decoding is supported for TDT decoder now"
        )

        B, S, *_ = features.shape

        if hidden_state is None:
            hidden_state = list([None] * B)

        if lengths is None:
            lengths = mx.array([S] * B)

        if last_token is None:
            last_token = list([None] * B)

        results = []
        for batch in range(B):
            hypothesis = []

            feature = features[batch : batch + 1]
            length = int(lengths[batch])

            step = 0
            new_symbols = 0

            while step < length:
                # decoder pass
                decoder_out, (hidden, cell) = self.decoder(
                    mx.array([[last_token[batch]]])
                    if last_token[batch] is not None
                    else None,
                    hidden_state[batch],
                )
                decoder_out = decoder_out.astype(feature.dtype)
                decoder_hidden = (
                    hidden.astype(feature.dtype),
                    cell.astype(feature.dtype),
                )

                # joint pass
                joint_out = self.joint(feature[:, step : step + 1], decoder_out)

                # sampling
                pred_token = int(
                    mx.argmax(joint_out[0, 0, :, : len(self.vocabulary) + 1])
                )
                decision = int(
                    mx.argmax(joint_out[0, 0, :, len(self.vocabulary) + 1 :])
                )

                # tdt decoding rule
                if pred_token != len(self.vocabulary):
                    hypothesis.append(
                        AlignedToken(
                            int(pred_token),
                            start=step
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            duration=self.durations[decision]
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            text=tokenizer.decode([pred_token], self.vocabulary),
                        )
                    )
                    last_token[batch] = pred_token
                    hidden_state[batch] = decoder_hidden

                step += self.durations[int(decision)]

                # prevent stucking rule
                new_symbols += 1

                if self.durations[int(decision)] != 0:
                    new_symbols = 0
                else:
                    if self.max_symbols is not None and self.max_symbols <= new_symbols:
                        step += 1
                        new_symbols = 0

            results.append(hypothesis)

        return results, hidden_state

    def generate(
        self, mel: mx.array, *, decoding_config: DecodingConfig = DecodingConfig()
    ) -> list[AlignedResult]:
        if len(mel.shape) == 2:
            mel = mx.expand_dims(mel, 0)

        features, lengths = self.encoder(mel)
        mx.eval(features, lengths)

        result, _ = self.decode(features, lengths, config=decoding_config)

        return [
            sentences_to_result(tokens_to_sentences(hypothesis))
            for hypothesis in result
        ]


class ParakeetRNNT(BaseParakeet):
    """MLX Implementation of Parakeet-RNNT Model"""

    def __init__(self, args: ParakeetRNNTArgs):
        super().__init__(args.preprocessor, args.encoder)

        self.vocabulary = args.joint.vocabulary
        self.max_symbols: int | None = (
            args.decoding.greedy.get("max_symbols", None)
            if args.decoding.greedy
            else None
        )

        self.decoder = PredictNetwork(args.decoder)
        self.joint = JointNetwork(args.joint)

    def decode(
        self,
        features: mx.array,
        lengths: Optional[mx.array] = None,
        last_token: Optional[list[Optional[int]]] = None,
        hidden_state: Optional[list[Optional[tuple[mx.array, mx.array]]]] = None,
        *,
        config: DecodingConfig = DecodingConfig(),
    ) -> tuple[list[list[AlignedToken]], list[Optional[tuple[mx.array, mx.array]]]]:
        """Run TDT decoder with features, optional length and decoder state. Outputs list[list[AlignedToken]] and updated hidden state"""
        assert config.decoding == "greedy", (
            "Only greedy decoding is supported for RNNT decoder now"
        )

        B, S, *_ = features.shape

        if hidden_state is None:
            hidden_state = list([None] * B)

        if lengths is None:
            lengths = mx.array([S] * B)

        if last_token is None:
            last_token = list([None] * B)

        results = []
        for batch in range(B):
            hypothesis = []

            feature = features[batch : batch + 1]
            length = int(lengths[batch])

            step = 0
            new_symbols = 0

            while step < length:
                # decoder pass
                decoder_out, (hidden, cell) = self.decoder(
                    mx.array([[last_token[batch]]])
                    if last_token[batch] is not None
                    else None,
                    hidden_state[batch],
                )
                decoder_out = decoder_out.astype(feature.dtype)
                decoder_hidden = (
                    hidden.astype(feature.dtype),
                    cell.astype(feature.dtype),
                )

                # joint pass
                joint_out = self.joint(feature[:, step : step + 1], decoder_out)

                # sampling
                pred_token = int(mx.argmax(joint_out[0, 0]))

                # rnnt decoding rule
                if pred_token != len(self.vocabulary):
                    hypothesis.append(
                        AlignedToken(
                            int(pred_token),
                            start=step
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            duration=1
                            * self.encoder_config.subsampling_factor
                            / self.preprocessor_config.sample_rate
                            * self.preprocessor_config.hop_length,  # hop
                            text=tokenizer.decode([pred_token], self.vocabulary),
                        )
                    )
                    last_token[batch] = pred_token
                    hidden_state[batch] = decoder_hidden

                    # prevent stucking
                    new_symbols += 1
                    if self.max_symbols is not None and self.max_symbols <= new_symbols:
                        step += 1
                        new_symbols = 0
                else:
                    step += 1
                    new_symbols = 0

            results.append(hypothesis)

        return results, hidden_state

    def generate(
        self, mel: mx.array, *, decoding_config: DecodingConfig = DecodingConfig()
    ) -> list[AlignedResult]:
        if len(mel.shape) == 2:
            mel = mx.expand_dims(mel, 0)

        features, lengths = self.encoder(mel)
        mx.eval(features, lengths)

        result, _ = self.decode(features, lengths, config=decoding_config)

        return [
            sentences_to_result(tokens_to_sentences(hypothesis))
            for hypothesis in result
        ]


class ParakeetCTC(BaseParakeet):
    """MLX Implementation of Parakeet-CTC Model"""

    def __init__(self, args: ParakeetCTCArgs):
        super().__init__(args.preprocessor, args.encoder)

        self.vocabulary = args.decoder.vocabulary

        self.decoder = ConvASRDecoder(args.decoder)

    def decode(
        self,
        features: mx.array,
        lengths: mx.array,
        *,
        config: DecodingConfig = DecodingConfig(),
    ) -> list[list[AlignedToken]]:
        """Run CTC decoder with features and lengths. Outputs list[list[AlignedToken]]."""
        B, S, *_ = features.shape

        logits = self.decoder(features)
        mx.eval(logits, lengths)

        results = []
        for batch in range(B):
            length = int(lengths[batch])
            predictions = logits[batch, :length]
            best_tokens = mx.argmax(predictions, axis=1)

            hypothesis = []
            token_boundaries = []
            prev_token = -1

            for t, token_id in enumerate(best_tokens):
                token_idx = int(token_id)

                if token_idx == len(self.vocabulary):
                    continue

                if token_idx == prev_token:
                    continue

                if prev_token != -1:
                    token_start_time = (
                        token_boundaries[-1][0]
                        * self.encoder_config.subsampling_factor
                        / self.preprocessor_config.sample_rate
                        * self.preprocessor_config.hop_length
                    )

                    token_end_time = (
                        t
                        * self.encoder_config.subsampling_factor
                        / self.preprocessor_config.sample_rate
                        * self.preprocessor_config.hop_length
                    )

                    token_duration = token_end_time - token_start_time

                    hypothesis.append(
                        AlignedToken(
                            prev_token,
                            start=token_start_time,
                            duration=token_duration,
                            text=tokenizer.decode([prev_token], self.vocabulary),
                        )
                    )

                token_boundaries.append((t, None))
                prev_token = token_idx

            if prev_token != -1:
                last_non_blank = length - 1
                for t in range(length - 1, token_boundaries[-1][0], -1):
                    if int(best_tokens[t]) != len(self.vocabulary):
                        last_non_blank = t
                        break

                token_start_time = (
                    token_boundaries[-1][0]
                    * self.encoder_config.subsampling_factor
                    / self.preprocessor_config.sample_rate
                    * self.preprocessor_config.hop_length
                )

                token_end_time = (
                    (last_non_blank + 1)
                    * self.encoder_config.subsampling_factor
                    / self.preprocessor_config.sample_rate
                    * self.preprocessor_config.hop_length
                )

                token_duration = token_end_time - token_start_time

                hypothesis.append(
                    AlignedToken(
                        prev_token,
                        start=token_start_time,
                        duration=token_duration,
                        text=tokenizer.decode([prev_token], self.vocabulary),
                    )
                )

            results.append(hypothesis)

        return results

    def generate(
        self, mel: mx.array, *, decoding_config: DecodingConfig = DecodingConfig()
    ) -> list[AlignedResult]:
        if len(mel.shape) == 2:
            mel = mx.expand_dims(mel, 0)

        features, lengths = self.encoder(mel)

        result = self.decode(features, lengths, config=decoding_config)

        return [
            sentences_to_result(tokens_to_sentences(hypothesis))
            for hypothesis in result
        ]


class ParakeetTDTCTC(ParakeetTDT):
    """MLX Implementation of Parakeet-TDT-CTC Model

    Has ConvASRDecoder decoder in `.ctc_decoder` but `.generate` uses TDT decoder all the times (Please open an issue if you need CTC decoder use-case!)"""

    def __init__(self, args: ParakeetTDTCTCArgs):
        super().__init__(args)

        self.ctc_decoder = ConvASRDecoder(args.aux_ctc.decoder)


# streaming
class StreamingParakeet:
    model: "BaseParakeet"
    cache: List[ConformerCache]

    audio_buffer: mx.array
    mel_buffer: Optional[mx.array]
    decoder_hidden: Optional[tuple[mx.array, mx.array]] = None
    last_token: Optional[int] = None

    finalized_tokens: list[AlignedToken]
    draft_tokens: list[AlignedToken]

    context_size: tuple[int, int]
    depth: int
    decoding_config: DecodingConfig
    keep_original_attention: bool = False

    def __init__(
        self,
        model: "BaseParakeet",
        context_size: tuple[int, int],
        depth: int = 1,
        *,
        keep_original_attention: bool = False,
        decoding_config: DecodingConfig = DecodingConfig(),
    ) -> None:
        self.context_size = context_size
        self.depth = depth
        self.decoding_config = decoding_config
        self.keep_original_attention = keep_original_attention

        self.model = model
        self.cache = [
            RotatingConformerCache(self.keep_size, cache_drop_size=self.drop_size)
            for _ in range(len(model.encoder.layers))
        ]

        self.audio_buffer = mx.array([])
        self.mel_buffer = None
        self.finalized_tokens = []
        self.draft_tokens = []

    def __enter__(self):
        if not self.keep_original_attention:
            self.model.encoder.set_attention_model(
                "rel_pos_local_attn", self.context_size
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.keep_original_attention:
            self.model.encoder.set_attention_model(
                "rel_pos"
            )  # hard-coded; might cache if there's actually new varient than rel_pos
        del self.audio_buffer
        del self.cache

        mx.clear_cache()

    @property
    def keep_size(self):
        """Indicates how many encoded feature frames to keep in KV cache"""
        return self.context_size[0]

    @property
    def drop_size(self):
        """Indicates how many encoded feature frames to drop"""
        return self.context_size[1] * self.depth

    @property
    def result(self) -> AlignedResult:
        """Transcription result"""
        return sentences_to_result(
            tokens_to_sentences(self.finalized_tokens + self.draft_tokens)
        )

    def add_audio(self, audio: mx.array) -> None:
        """Takes portion of audio and transcribe it.

        `audio` must be 1D array"""

        self.audio_buffer = mx.concat(
            [
                self.audio_buffer,
                audio,
            ],
            axis=0,
        )
        mel = get_logmel(
            self.audio_buffer[
                : (
                    len(self.audio_buffer)
                    // self.model.preprocessor_config.hop_length
                    * self.model.preprocessor_config.hop_length
                )
            ],
            self.model.preprocessor_config,
        )

        if self.mel_buffer is None:  # init
            self.mel_buffer = mel
        else:
            self.mel_buffer = mx.concat([self.mel_buffer, mel], axis=1)

        self.audio_buffer = self.audio_buffer[
            (mel.shape[1] * self.model.preprocessor_config.hop_length) :
        ]

        features, lengths = self.model.encoder(
            self.mel_buffer[
                :,
                : (
                    self.mel_buffer.shape[1]
                    // self.model.encoder_config.subsampling_factor
                    * self.model.encoder_config.subsampling_factor
                ),
            ],
            cache=self.cache,
        )
        mx.eval(features, lengths)
        length = int(lengths[0])

        # cache will automatically dropped in cache level
        leftover = self.mel_buffer.shape[1] - (
            length * self.model.encoder_config.subsampling_factor
        )
        self.mel_buffer = self.mel_buffer[
            :,
            -(
                self.drop_size * self.model.encoder_config.subsampling_factor + leftover
            ) :,
        ]

        # we decode in two phase
        # first phase: finalized region decode
        # second phase: draft region decode (will be dropped)
        finalized_length = max(0, length - self.drop_size)

        if isinstance(self.model, ParakeetTDT) or isinstance(self.model, ParakeetRNNT):
            finalized_tokens, finalized_state = self.model.decode(
                features,
                mx.array([finalized_length]),
                [self.last_token],
                [self.decoder_hidden],
                config=self.decoding_config,
            )

            self.decoder_hidden = finalized_state[0]
            self.last_token = (
                finalized_tokens[0][-1].id if len(finalized_tokens[0]) > 0 else None
            )

            draft_tokens, _ = self.model.decode(
                features[:, finalized_length:],
                mx.array(
                    [
                        features[:, finalized_length:].shape[1]
                    ]  # i believe in lazy evaluation
                ),
                [self.last_token],
                [self.decoder_hidden],
                config=self.decoding_config,
            )

            self.finalized_tokens.extend(finalized_tokens[0])
            self.draft_tokens = draft_tokens[0]
        elif isinstance(self.model, ParakeetCTC):
            finalized_tokens = self.model.decode(
                features, mx.array([finalized_length]), config=self.decoding_config
            )

            draft_tokens = self.model.decode(
                features[:, finalized_length:],
                mx.array(
                    [
                        features[:, finalized_length:].shape[1]
                    ]  # i believe in lazy evaluation
                ),
                config=self.decoding_config,
            )

            self.finalized_tokens.extend(finalized_tokens[0])
            self.draft_tokens = draft_tokens[0]
        else:
            raise NotImplementedError("This model does not support real-time decoding")
````
