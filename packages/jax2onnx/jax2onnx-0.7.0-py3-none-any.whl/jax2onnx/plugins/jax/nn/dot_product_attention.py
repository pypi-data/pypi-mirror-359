# file: jax2onnx/plugins/jax/nn/dot_product_attention.py
# --------------------------------------------------------------------------- #
#   Dot-Product-Attention primitive → ONNX                                    #
# --------------------------------------------------------------------------- #
from typing import TYPE_CHECKING

import numpy as np
from jax import numpy as jnp
from jax import core, nn
from jax.extend.core import Primitive
from onnx import TensorProto, helper

from jax2onnx.plugin_system import PrimitiveLeafPlugin, register_primitive

if TYPE_CHECKING:  # pragma: no cover
    from jax2onnx.converter.jaxpr_converter import Jaxpr2OnnxConverter

# --------------------------------------------------------------------------- #
#   Ensure jnp.einsum has a batching rule (needed by reference implementation) #
# --------------------------------------------------------------------------- #
from jax.interpreters import batching


# Callable definitions for test cases
def dpa_with_mask(q, k, v, mask):
    """Wrapper for dot_product_attention with a boolean mask."""
    return nn.dot_product_attention(q, k, v, mask=mask)


def dpa_with_causal_mask(q, k, v):
    """Wrapper for dot_product_attention with causal masking."""
    return nn.dot_product_attention(q, k, v, is_causal=True)


def dpa_with_padding_mask(q, k, v, q_len, kv_len):
    """Wrapper for dpa with padding masks."""
    return nn.dot_product_attention(
        q, k, v, query_seq_lengths=q_len, key_value_seq_lengths=kv_len
    )


def dpa_with_local_window_mask(q, k, v):
    """Wrapper for dpa with a local window mask."""
    return nn.dot_product_attention(q, k, v, local_window_size=(1, 1))


# --------------------------------------------------------------------------- #
#   JAX primitive stub                                                        #
# --------------------------------------------------------------------------- #
nn.dot_product_attention_p = Primitive("nn.dot_product_attention")
nn.dot_product_attention_p.multiple_results = False


@register_primitive(
    jaxpr_primitive=nn.dot_product_attention_p.name,
    jax_doc=(
        "https://flax.readthedocs.io/en/latest/api_reference/"
        "flax.nnx/nn/attention.html#flax.nn.dot_product_attention"
    ),
    onnx=[
        {
            "component": "Transpose",
            "doc": "https://onnx.ai/onnx/operators/onnx__Transpose.html",
        },
        {
            "component": "MatMul",
            "doc": "https://onnx.ai/onnx/operators/onnx__MatMul.html",
        },
        {"component": "Mul", "doc": "https://onnx.ai/onnx/operators/onnx__Mul.html"},
        {"component": "Add", "doc": "https://onnx.ai/onnx/operators/onnx__Add.html"},
        {"component": "Not", "doc": "https://onnx.ai/onnx/operators/onnx__Not.html"},
        {"component": "Cast", "doc": "https://onnx.ai/onnx/operators/onnx__Cast.html"},
        {
            "component": "Softmax",
            "doc": "https://onnx.ai/onnx/operators/onnx__Softmax.html",
        },
        {
            "component": "Where",
            "doc": "https://onnx.ai/onnx/operators/onnx__Where.html",
        },
    ],
    since="v0.1.0",
    context="primitives.nn",
    component="dot_product_attention",
    testcases=[
        {
            "testcase": "dpa_basic",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(2, 4, 8, 32), (2, 4, 8, 32), (2, 4, 8, 32)],
        },
        {
            "testcase": "dpa_diff_heads_embed",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(1, 2, 4, 16), (1, 2, 4, 16), (1, 2, 4, 16)],
        },
        {
            "testcase": "dpa_batch4_seq16",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(4, 2, 16, 8), (4, 2, 16, 8), (4, 2, 16, 8)],
        },
        {
            "testcase": "dpa_float64",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(2, 4, 8, 32), (2, 4, 8, 32), (2, 4, 8, 32)],
            "input_dtype": np.float64,
        },
        {
            "testcase": "dpa_heads1_embed4",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(2, 1, 8, 4), (2, 1, 8, 4), (2, 1, 8, 4)],
        },
        {
            "testcase": "dpa_heads8_embed8",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(2, 8, 8, 8), (2, 8, 8, 8), (2, 8, 8, 8)],
        },
        {
            "testcase": "dpa_batch1_seq2",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(1, 2, 2, 8), (1, 2, 2, 8), (1, 2, 2, 8)],
        },
        {
            "testcase": "dpa_batch8_seq4",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(8, 2, 4, 16), (8, 2, 4, 16), (8, 2, 4, 16)],
        },
        {
            "testcase": "dpa_axis1",
            "callable": lambda q, k, v: nn.dot_product_attention(q, k, v),
            "input_shapes": [(2, 4, 8, 32), (2, 4, 8, 32), (2, 4, 8, 32)],
        },
        {
            "testcase": "dpa_with_tensor_mask",
            "callable": dpa_with_mask,
            "input_shapes": [
                (2, 8, 4, 16),
                (2, 16, 4, 16),
                (2, 16, 4, 16),
                (2, 4, 8, 16),
            ],
            "input_dtypes": [np.float32, np.float32, np.float32, np.bool_],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_tiny_mask_all_valid",
            "callable": dpa_with_mask,
            "input_values": [
                np.arange(1 * 2 * 1 * 4).reshape((1, 2, 1, 4)).astype(np.float32),
                np.arange(1 * 3 * 1 * 4).reshape((1, 3, 1, 4)).astype(np.float32),
                np.arange(1 * 3 * 1 * 4).reshape((1, 3, 1, 4)).astype(np.float32),
                np.ones((1, 1, 2, 3), dtype=bool),
            ],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_tiny_mask_mixed",
            "callable": dpa_with_mask,
            "input_values": [
                np.arange(1 * 2 * 1 * 4).reshape((1, 2, 1, 4)).astype(np.float32),
                np.arange(1 * 3 * 1 * 4).reshape((1, 3, 1, 4)).astype(np.float32),
                np.arange(1 * 3 * 1 * 4).reshape((1, 3, 1, 4)).astype(np.float32),
                np.array([[[[True, False, True], [False, True, False]]]], dtype=bool),
            ],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_one_false",
            "callable": dpa_with_mask,
            "input_values": [
                np.array([[[[1.0, 2.0, 3.0, 4.0]]]], dtype=np.float32),
                np.array(
                    [[[[1.0, 0.0, 0.0, 0.0]], [[0.0, 1.0, 0.0, 0.0]]]], dtype=np.float32
                ),
                np.array(
                    [[[[10.0, 20.0, 30.0, 40.0]], [[50.0, 60.0, 70.0, 80.0]]]],
                    dtype=np.float32,
                ),
                np.array([[[[True, False]]]], dtype=bool),
            ],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_mostly_false",
            "callable": dpa_with_mask,
            "input_values": [
                np.ones((1, 1, 1, 4), np.float32),
                np.ones((1, 2, 1, 4), np.float32),
                np.ones((1, 2, 1, 4), np.float32) * 7,
                np.array([[[[False, True]]]], dtype=bool),  # Not all entries are masked
            ],
            "expected_output_numpy": [np.zeros((1, 1, 1, 4), np.float32)],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_with_causal_mask",
            "callable": dpa_with_causal_mask,
            "input_shapes": [(2, 8, 4, 16), (2, 8, 4, 16), (2, 8, 4, 16)],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_with_padding_mask",
            "callable": dpa_with_padding_mask,
            "input_values": [
                np.random.randn(2, 8, 4, 16).astype(np.float32),
                np.random.randn(2, 8, 4, 16).astype(np.float32),
                np.random.randn(2, 8, 4, 16).astype(np.float32),
                np.array([8, 4], dtype=np.int32),
                np.array([8, 7], dtype=np.int32),
            ],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
        {
            "testcase": "dpa_with_local_window_mask",
            "callable": dpa_with_local_window_mask,
            "input_shapes": [(1, 16, 1, 4), (1, 16, 1, 4), (1, 16, 1, 4)],
            "atol_f64": 1e-6,  # Absolute tolerance for float64
            "rtol_f64": 1e-6,  # Relative tolerance for float64
        },
    ],
)
class DotProductAttentionPlugin(PrimitiveLeafPlugin):
    @staticmethod
    def abstract_eval(q, k, v, *args, **kwargs):
        return core.ShapedArray(q.shape, q.dtype)

    def to_onnx(self, s: "Jaxpr2OnnxConverter", node_inputs, node_outputs, params):
        q, k, v, *optional_inputs = node_inputs
        out_var = node_outputs[0]

        q_name, k_name, v_name = map(s.get_name, (q, k, v))
        out_name = s.get_name(out_var)
        B, T, N, H = q.aval.shape
        _, S, _, _ = k.aval.shape
        np_dtype = q.aval.dtype
        s.builder._numpy_dtype_to_onnx(np_dtype)

        q_t = s.get_unique_name("q_T")
        k_t = s.get_unique_name("k_T")
        s.add_node(helper.make_node("Transpose", [q_name], [q_t], perm=[0, 2, 1, 3]))
        s.add_node(helper.make_node("Transpose", [k_name], [k_t], perm=[0, 2, 3, 1]))
        s.add_shape_info(q_t, (B, N, T, H), np_dtype)
        s.add_shape_info(k_t, (B, N, H, S), np_dtype)

        logits = s.get_unique_name("attn_scores")
        s.add_node(helper.make_node("MatMul", [q_t, k_t], [logits]))
        s.add_shape_info(logits, (B, N, T, S), np_dtype)

        scale_const = s.get_constant_name(np.array(1.0 / np.sqrt(H), dtype=np_dtype))
        scaled_scores = s.get_unique_name("scaled_scores")
        s.add_node(helper.make_node("Mul", [logits, scale_const], [scaled_scores]))
        s.add_shape_info(scaled_scores, (B, N, T, S), np_dtype)

        final_logits = scaled_scores
        if optional_inputs:
            mask_var = optional_inputs[0]
            mask_name = s.get_name(mask_var)
            mask_bool_name = s.get_unique_name("mask_bool")
            s.add_node(
                helper.make_node(
                    "Cast", [mask_name], [mask_bool_name], to=TensorProto.BOOL
                )
            )
            s.add_shape_info(mask_bool_name, mask_var.aval.shape, dtype=bool)
            large_negative_number_const = s.get_constant_name(
                np.array(-1e9, dtype=np_dtype)
            )
            masked_logits = s.get_unique_name("masked_logits")
            s.add_node(
                helper.make_node(
                    "Where",
                    inputs=[mask_bool_name, scaled_scores, large_negative_number_const],
                    outputs=[masked_logits],
                )
            )
            s.add_shape_info(masked_logits, (B, N, T, S), np_dtype)
            final_logits = masked_logits

        weights = s.get_unique_name("attn_weights")
        s.add_node(helper.make_node("Softmax", [final_logits], [weights], axis=-1))
        s.add_shape_info(weights, (B, N, T, S), np_dtype)

        v_t = s.get_unique_name("v_T")
        out_t = s.get_unique_name("out_T")
        s.add_node(helper.make_node("Transpose", [v_name], [v_t], perm=[0, 2, 1, 3]))
        s.add_shape_info(v_t, (B, N, S, H), np_dtype)
        s.add_node(helper.make_node("MatMul", [weights, v_t], [out_t]))
        s.add_shape_info(out_t, (B, N, T, H), np_dtype)
        s.add_node(
            helper.make_node("Transpose", [out_t], [out_name], perm=[0, 2, 1, 3])
        )
        s.add_shape_info(out_name, (B, T, N, H), np_dtype)

    @staticmethod
    def _dot_product_attention(q, k, v, mask=None, axis=-1):
        if mask is not None:
            return nn.dot_product_attention_p.bind(q, k, v, mask, axis=axis)
        return nn.dot_product_attention_p.bind(q, k, v, axis=axis)

    @staticmethod
    def get_monkey_patch():
        def patched(q, k, v, mask=None, axis=-1, **kwargs):
            return DotProductAttentionPlugin._dot_product_attention(
                q, k, v, mask, axis=axis
            )

        return patched

    @staticmethod
    def patch_info():
        return {
            "patch_targets": [nn],
            "patch_function": lambda _: DotProductAttentionPlugin.get_monkey_patch(),
            "target_attribute": "dot_product_attention",
        }


# attach abstract-eval
nn.dot_product_attention_p.def_abstract_eval(DotProductAttentionPlugin.abstract_eval)


# --------------------------- batching rule -----------------------------------
def dpa_batch(xs, dims, *, axis=-1):
    assert len(set(d for d in dims if d is not None)) <= 1
    q, k, v, *rest = xs
    bdim = next((d for d in dims if d is not None), None)

    if bdim is not None and bdim != 0:
        q = jnp.moveaxis(q, bdim, 0)
        k = jnp.moveaxis(k, bdim, 0)
        v = jnp.moveaxis(v, bdim, 0)
        if rest:
            rest = [
                jnp.moveaxis(r, d, 0) if d is not None else r
                for r, d in zip(rest, dims[3:])
            ]

    out = nn.dot_product_attention(q, k, v, *rest, axis=axis)
    return out, 0


batching.primitive_batchers[nn.dot_product_attention_p] = dpa_batch
