# Copyright (C) 2025 Dexmate Inc.
#
# This software is dual-licensed:
#
# 1. GNU Affero General Public License v3.0 (AGPL-3.0)
#    See LICENSE-AGPL for details
#
# 2. Commercial License
#    For commercial licensing terms, contact: contact@dexmate.ai

from dataclasses import dataclass, field
from typing import ClassVar

from omegaconf import OmegaConf

from dexcontrol.utils.os_utils import get_robot_model

from .core import (
    ArmConfig,
    BatteryConfig,
    ChassisConfig,
    EStopConfig,
    HandConfig,
    HeadConfig,
    HeartbeatConfig,
    TorsoConfig,
)
from .sensors.vega_sensors import VegaSensorsConfig


@dataclass
class VegaConfig:
    """Base configuration for Vega robots.

    This class serves as the base configuration for all Vega robot variants.
    Different robot variants can extend this class or be loaded through the
    factory function get_vega_config().
    """

    # Registry to store variant-specific configuration classes
    _variants: ClassVar[dict[str, type["VegaConfig"]]] = {}

    sensors: VegaSensorsConfig = field(default_factory=VegaSensorsConfig)
    left_arm: ArmConfig = field(
        default_factory=lambda: ArmConfig(
            state_sub_topic="state/arm/left",
            control_pub_topic="control/arm/left",
            set_mode_query="mode/arm/left",
            wrench_sub_topic="state/wrench/left",
            joint_name=[f"L_arm_j{i + 1}" for i in range(7)],
            pose_pool={
                "folded": [1.57079, 0.0, 0, -3.1, 0, 0, -0.69813],
                "folded_closed_hand": [1.57079, 0.0, 0, -3.1, 0, 0, -0.9],
                "L_shape": [0.064, -0.3, 0.0, -1.556, 1.271, 0.0, 0.0],
                "zero": [-1.57079, 0.0, 0, 0.0, 0, 0, 0.0],
            },
        )
    )
    right_arm: ArmConfig = field(
        default_factory=lambda: ArmConfig(
            state_sub_topic="state/arm/right",
            control_pub_topic="control/arm/right",
            set_mode_query="mode/arm/right",
            wrench_sub_topic="state/wrench/right",
            joint_name=[f"R_arm_j{i + 1}" for i in range(7)],
            pose_pool={
                "folded": [-1.57079, 0.0, 0, -3.1, 0, 0, 0.69813],
                "folded_closed_hand": [-1.57079, 0.0, 0, -3.1, 0, 0, 0.9],
                "L_shape": [-0.064, 0.3, 0.0, -1.556, -1.271, 0.0, 0.0],
                "zero": [1.57079, 0.0, 0, 0.0, 0, 0, 0.0],
            },
        )
    )
    left_hand: HandConfig = field(
        default_factory=lambda: HandConfig(
            state_sub_topic="state/hand/left",
            control_pub_topic="control/hand/left",
            joint_name=[
                "L_th_j1",
                "L_ff_j1",
                "L_mf_j1",
                "L_rf_j1",
                "L_lf_j1",
                "L_th_j0",
            ],
        )
    )
    right_hand: HandConfig = field(
        default_factory=lambda: HandConfig(
            state_sub_topic="state/hand/right",
            control_pub_topic="control/hand/right",
            joint_name=[
                "R_th_j1",
                "R_ff_j1",
                "R_mf_j1",
                "R_rf_j1",
                "R_lf_j1",
                "R_th_j0",
            ],
        )
    )
    head: HeadConfig = field(default_factory=HeadConfig)
    torso: TorsoConfig = field(default_factory=TorsoConfig)
    chassis: ChassisConfig = field(default_factory=ChassisConfig)

    # Misc
    battery: BatteryConfig = field(default_factory=BatteryConfig)
    estop: EStopConfig = field(default_factory=EStopConfig)
    heartbeat: HeartbeatConfig = field(default_factory=HeartbeatConfig)

    # Queries
    version_info_name: str = "info/version"
    status_info_name: str = "info/status"
    reboot_query_name: str = "system/reboot"
    clear_error_query_name: str = "system/clear_error"
    led_query_name: str = "system/led"

    @classmethod
    def register_variant(
        cls, variant_name: str, variant_cls: type["VegaConfig"]
    ) -> None:
        """Register a variant configuration class.

        Args:
            variant_name: Name of the robot variant.
            variant_cls: Configuration class for the variant.
        """
        cls._variants[variant_name] = variant_cls


@dataclass
class Vega1Config(VegaConfig):
    """Configuration specific to the Vega 1 robot variant."""

    left_arm: ArmConfig = field(
        default_factory=lambda: ArmConfig(
            state_sub_topic="state/arm/left",
            control_pub_topic="control/arm/left",
            set_mode_query="mode/arm/left",
            wrench_sub_topic="state/wrench/left",
            joint_name=[f"L_arm_j{i + 1}" for i in range(7)],
            pose_pool={
                "folded": [1.57079, 0.0, 0, -3.1, 0, 0, -0.69813],
                "folded_closed_hand": [1.57079, 0.0, 0, -3.1, 0, 0, -0.9],
                "L_shape": [0.064, 0.3, 0.0, -1.556, 1.271, 0.0, 0.0],
                "zero": [-1.57079, 0.0, 0, 0.0, 0, 0, 0.0],
            },
        )
    )
    right_arm: ArmConfig = field(
        default_factory=lambda: ArmConfig(
            state_sub_topic="state/arm/right",
            control_pub_topic="control/arm/right",
            set_mode_query="mode/arm/right",
            wrench_sub_topic="state/wrench/right",
            joint_name=[f"R_arm_j{i + 1}" for i in range(7)],
            pose_pool={
                "folded": [-1.57079, 0.0, 0, -3.1, 0, 0, 0.69813],
                "folded_closed_hand": [-1.57079, 0.0, 0, -3.1, 0, 0, 0.9],
                "L_shape": [-0.064, -0.3, 0.0, -1.556, -1.271, 0.0, 0.0],
                "zero": [1.57079, 0.0, 0, 0.0, 0, 0, 0.0],
            },
        )
    )
    chassis: ChassisConfig = field(
        default_factory=lambda: ChassisConfig(
            wheels_dist=0.45,
        )
    )
    head: HeadConfig = field(
        default_factory=lambda: HeadConfig(
            joint_limit_lower=[-1.483, -2.792, -1.378],
            joint_limit_upper=[1.483, 2.792, 1.483],
        )
    )


# Register variant configurations
VegaConfig.register_variant("vega-rc1", VegaConfig)
VegaConfig.register_variant("vega-rc2", VegaConfig)
VegaConfig.register_variant("vega-1", Vega1Config)


def get_vega_config(variant: str | None = None) -> VegaConfig:
    """Get the configuration for a specific Vega robot variant.

    Args:
        variant: The robot variant name (e.g., "rc2", "vega-1").
                If None, returns the base VegaConfig.

    Returns:
        The configuration for the specified Vega robot variant as an OmegaConf object.
    """
    if variant is None:
        variant = get_robot_model()

    if variant in VegaConfig._variants:
        config_class = VegaConfig._variants[variant]
    else:
        raise ValueError(
            f"Unknown robot variant: {variant}. "
            f"Available variants: {list(VegaConfig._variants.keys())}"
        )

    config = config_class()
    return OmegaConf.structured(config)


def get_default_vega_config() -> VegaConfig:
    """Get the default Vega robot configuration.

    This is kept for backward compatibility.

    Returns:
        The configuration for the default Vega robot as an OmegaConf object.
    """
    return get_vega_config("vega-1")
