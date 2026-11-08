from __future__ import annotations

from typing import Literal, TypeAlias, TypedDict, TypeVar

from ._values import (
    Angle,
    Fractions,
    Frequency,
    Length,
    Percentage,
    PropertyValue,
    RawCSS,
    Resolution,
    Time,
)

# Generated from https://github.com/mdn/data CSS grammars (CC0).
# Tuples represent space-separated values; lists represent comma-separated values.

_T = TypeVar("_T")
_Pair: TypeAlias = _T | tuple[_T, _T]
_Triple: TypeAlias = _Pair[_T] | tuple[_T, _T, _T]
_Quad: TypeAlias = _Triple[_T] | tuple[_T, _T, _T, _T]
_Sequence: TypeAlias = _T | tuple[_T, ...]
_Comma: TypeAlias = _T | list[_T]

_AccentColor: TypeAlias = str
_AdditiveSymbols: TypeAlias = _Comma[tuple[int | str, ...]]
_AlignContent: TypeAlias = Literal[
    "baseline",
    "center",
    "end",
    "first baseline",
    "flex-end",
    "flex-start",
    "last baseline",
    "normal",
    "safe center",
    "safe end",
    "safe flex-end",
    "safe flex-start",
    "safe start",
    "space-around",
    "space-between",
    "space-evenly",
    "start",
    "stretch",
    "unsafe center",
    "unsafe end",
    "unsafe flex-end",
    "unsafe flex-start",
    "unsafe start",
]
_AlignItems: TypeAlias = Literal[
    "anchor-center",
    "baseline",
    "center",
    "end",
    "first baseline",
    "flex-end",
    "flex-start",
    "last baseline",
    "normal",
    "safe center",
    "safe end",
    "safe flex-end",
    "safe flex-start",
    "safe self-end",
    "safe self-start",
    "safe start",
    "self-end",
    "self-start",
    "start",
    "stretch",
    "unsafe center",
    "unsafe end",
    "unsafe flex-end",
    "unsafe flex-start",
    "unsafe self-end",
    "unsafe self-start",
    "unsafe start",
]
_AlignSelf: TypeAlias = Literal[
    "anchor-center",
    "auto",
    "baseline",
    "center",
    "end",
    "first baseline",
    "flex-end",
    "flex-start",
    "last baseline",
    "normal",
    "safe center",
    "safe end",
    "safe flex-end",
    "safe flex-start",
    "safe self-end",
    "safe self-start",
    "safe start",
    "self-end",
    "self-start",
    "start",
    "stretch",
    "unsafe center",
    "unsafe end",
    "unsafe flex-end",
    "unsafe flex-start",
    "unsafe self-end",
    "unsafe self-start",
    "unsafe start",
]
_AlignTracks: TypeAlias = _Comma[
    Literal[
        "baseline",
        "center",
        "end",
        "first baseline",
        "flex-end",
        "flex-start",
        "last baseline",
        "normal",
        "safe center",
        "safe end",
        "safe flex-end",
        "safe flex-start",
        "safe start",
        "space-around",
        "space-between",
        "space-evenly",
        "start",
        "stretch",
        "unsafe center",
        "unsafe end",
        "unsafe flex-end",
        "unsafe flex-start",
        "unsafe start",
    ]
]
_AlignmentBaseline: TypeAlias = Literal[
    "alphabetic",
    "baseline",
    "central",
    "ideographic",
    "mathematical",
    "middle",
    "text-after-edge",
    "text-before-edge",
]
_All: TypeAlias = Literal[
    "inherit", "initial", "revert", "revert-layer", "unset"
]
_AnchorName: TypeAlias = Literal["none"] | _Comma[str]
_AnchorScope: TypeAlias = Literal["all", "none"] | _Comma[str]
_Animation: TypeAlias = _Comma[
    RawCSS
    | _Comma[Literal["auto"] | Time]
    | _Comma[Time]
    | float
    | str
    | tuple[RawCSS | Time | float | str, ...]
]
_AnimationComposition: TypeAlias = _Comma[
    Literal["accumulate", "add", "replace"]
]
_AnimationDelay: TypeAlias = _Comma[Time]
_AnimationDirection: TypeAlias = _Comma[
    Literal["alternate", "alternate-reverse", "normal", "reverse"]
]
_AnimationDuration: TypeAlias = _Comma[Literal["auto"] | Time]
_AnimationFillMode: TypeAlias = _Comma[
    Literal["backwards", "both", "forwards", "none"]
]
_AnimationIterationCount: TypeAlias = _Comma[Literal["infinite"] | float]
_AnimationName: TypeAlias = _Comma[str]
_AnimationPlayState: TypeAlias = _Comma[Literal["paused", "running"]]
_AnimationRange: TypeAlias = _Comma[
    _Comma[
        Length
        | Literal[
            "contain",
            "cover",
            "entry",
            "entry-crossing",
            "exit",
            "exit-crossing",
            "normal",
        ]
        | Literal[0]
        | Percentage
        | tuple[
            Length
            | Literal[
                "contain",
                "cover",
                "entry",
                "entry-crossing",
                "exit",
                "exit-crossing",
            ]
            | Literal[0]
            | Percentage,
            ...,
        ]
    ]
    | tuple[
        Length
        | Literal[
            "contain",
            "cover",
            "entry",
            "entry-crossing",
            "exit",
            "exit-crossing",
            "normal",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_AnimationRangeEnd: TypeAlias = _Comma[
    Length
    | Literal[
        "contain",
        "cover",
        "entry",
        "entry-crossing",
        "exit",
        "exit-crossing",
        "normal",
    ]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal[
            "contain",
            "cover",
            "entry",
            "entry-crossing",
            "exit",
            "exit-crossing",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_AnimationRangeStart: TypeAlias = _AnimationRangeEnd
_AnimationTimeline: TypeAlias = _Comma[RawCSS | str]
_AnimationTimingFunction: TypeAlias = _Comma[
    Literal[
        "ease",
        "ease-in",
        "ease-in-out",
        "ease-out",
        "linear",
        "step-end",
        "step-start",
    ]
    | RawCSS
]
_AnimationTrigger: TypeAlias = _Comma[
    Literal["none"] | _Sequence[tuple[str, ...]]
]
_Appearance: TypeAlias = Literal[
    "auto",
    "button",
    "checkbox",
    "listbox",
    "menulist",
    "menulist-button",
    "meter",
    "none",
    "progress-bar",
    "radio",
    "searchfield",
    "textarea",
    "textfield",
]
_AscentOverride: TypeAlias = Literal["normal"] | Percentage
_AspectRatio: TypeAlias = (
    Literal["auto"]
    | float
    | tuple[Literal["/", "auto"] | float, ...]
    | tuple[Literal["/"] | float, ...]
)
_BackdropFilter: TypeAlias = Literal["none"] | _Sequence[RawCSS | str]
_BackfaceVisibility: TypeAlias = Literal["hidden", "visible"]
_Background: TypeAlias = _Comma[
    Length
    | Literal[0]
    | Percentage
    | str
    | tuple[
        Length
        | Literal[
            "/",
            "auto",
            "bottom",
            "center",
            "contain",
            "cover",
            "left",
            "right",
            "top",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[Length | Literal[0] | Percentage | str, ...]
]
_BackgroundAttachment: TypeAlias = _Comma[Literal["fixed", "local", "scroll"]]
_BackgroundBlendMode: TypeAlias = _Comma[
    Literal[
        "color",
        "color-burn",
        "color-dodge",
        "darken",
        "difference",
        "exclusion",
        "hard-light",
        "hue",
        "lighten",
        "luminosity",
        "multiply",
        "normal",
        "overlay",
        "saturation",
        "screen",
        "soft-light",
    ]
]
_BackgroundClip: TypeAlias = _Comma[
    Literal["border-area", "border-box", "content-box", "padding-box", "text"]
]
_BackgroundColor: TypeAlias = str
_BackgroundImage: TypeAlias = _Comma[str]
_BackgroundOrigin: TypeAlias = _Comma[
    Literal["border-box", "content-box", "padding-box"]
]
_BackgroundPosition: TypeAlias = _Comma[
    Length
    | Literal["bottom", "center", "left", "right", "top"]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_BackgroundPositionX: TypeAlias = _Comma[
    Length
    | Literal["center", "left", "right", "x-end", "x-start"]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["left", "right", "x-end", "x-start"]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_BackgroundPositionY: TypeAlias = _Comma[
    Length
    | Literal["bottom", "center", "top", "y-end", "y-start"]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "top", "y-end", "y-start"]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_BackgroundRepeat: TypeAlias = _Comma[
    Literal[
        "no-repeat",
        "no-repeat no-repeat",
        "no-repeat repeat",
        "no-repeat round",
        "no-repeat space",
        "repeat",
        "repeat no-repeat",
        "repeat repeat",
        "repeat round",
        "repeat space",
        "repeat-x",
        "repeat-y",
        "round",
        "round no-repeat",
        "round repeat",
        "round round",
        "round space",
        "space",
        "space no-repeat",
        "space repeat",
        "space round",
        "space space",
    ]
]
_BackgroundSize: TypeAlias = _Comma[
    Literal["contain", "cover"]
    | _Pair[Length | Literal["auto"] | Literal[0] | Percentage]
]
_BasePalette: TypeAlias = Literal["dark", "light"] | int
_BaselineShift: TypeAlias = (
    Length | Literal["baseline", "sub", "super"] | Literal[0] | Percentage
)
_BaselineSource: TypeAlias = Literal["auto", "first", "last"]
_Bleed: TypeAlias = Length | Literal["auto"] | Literal[0]
_BlockSize: TypeAlias = (
    Length
    | Literal["auto", "fit-content", "max-content", "min-content"]
    | Literal[0]
    | Percentage
    | RawCSS
)
_Border: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderBlock: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderBlockColor: TypeAlias = _Pair[str]
_BorderBlockEnd: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderBlockEndColor: TypeAlias = str
_BorderBlockEndStyle: TypeAlias = Literal[
    "dashed",
    "dotted",
    "double",
    "groove",
    "hidden",
    "inset",
    "none",
    "outset",
    "ridge",
    "solid",
]
_BorderBlockEndWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderBlockStart: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderBlockStartColor: TypeAlias = str
_BorderBlockStartStyle: TypeAlias = _BorderBlockEndStyle
_BorderBlockStartWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderBlockStyle: TypeAlias = Literal[
    "dashed",
    "dashed dashed",
    "dashed dotted",
    "dashed double",
    "dashed groove",
    "dashed hidden",
    "dashed inset",
    "dashed none",
    "dashed outset",
    "dashed ridge",
    "dashed solid",
    "dotted",
    "dotted dashed",
    "dotted dotted",
    "dotted double",
    "dotted groove",
    "dotted hidden",
    "dotted inset",
    "dotted none",
    "dotted outset",
    "dotted ridge",
    "dotted solid",
    "double",
    "double dashed",
    "double dotted",
    "double double",
    "double groove",
    "double hidden",
    "double inset",
    "double none",
    "double outset",
    "double ridge",
    "double solid",
    "groove",
    "groove dashed",
    "groove dotted",
    "groove double",
    "groove groove",
    "groove hidden",
    "groove inset",
    "groove none",
    "groove outset",
    "groove ridge",
    "groove solid",
    "hidden",
    "hidden dashed",
    "hidden dotted",
    "hidden double",
    "hidden groove",
    "hidden hidden",
    "hidden inset",
    "hidden none",
    "hidden outset",
    "hidden ridge",
    "hidden solid",
    "inset",
    "inset dashed",
    "inset dotted",
    "inset double",
    "inset groove",
    "inset hidden",
    "inset inset",
    "inset none",
    "inset outset",
    "inset ridge",
    "inset solid",
    "none",
    "none dashed",
    "none dotted",
    "none double",
    "none groove",
    "none hidden",
    "none inset",
    "none none",
    "none outset",
    "none ridge",
    "none solid",
    "outset",
    "outset dashed",
    "outset dotted",
    "outset double",
    "outset groove",
    "outset hidden",
    "outset inset",
    "outset none",
    "outset outset",
    "outset ridge",
    "outset solid",
    "ridge",
    "ridge dashed",
    "ridge dotted",
    "ridge double",
    "ridge groove",
    "ridge hidden",
    "ridge inset",
    "ridge none",
    "ridge outset",
    "ridge ridge",
    "ridge solid",
    "solid",
    "solid dashed",
    "solid dotted",
    "solid double",
    "solid groove",
    "solid hidden",
    "solid inset",
    "solid none",
    "solid outset",
    "solid ridge",
    "solid solid",
]
_BorderBlockWidth: TypeAlias = _Pair[
    Length | Literal["medium", "thick", "thin"] | Literal[0]
]
_BorderBottom: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderBottomColor: TypeAlias = str
_BorderBottomLeftRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderBottomRightRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderBottomStyle: TypeAlias = _BorderBlockEndStyle
_BorderBottomWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderCollapse: TypeAlias = Literal["collapse", "separate"]
_BorderColor: TypeAlias = _Quad[str]
_BorderEndEndRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderEndStartRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderImage: TypeAlias = (
    _Quad[Percentage | float]
    | str
    | tuple[Length | Literal["/", "auto", "fill"] | Percentage | float, ...]
    | tuple[Length | Percentage | float | str, ...]
    | tuple[Literal["fill"] | Percentage | float, ...]
)
_BorderImageOutset: TypeAlias = _Quad[Length | float]
_BorderImageRepeat: TypeAlias = Literal[
    "repeat",
    "repeat repeat",
    "repeat round",
    "repeat space",
    "repeat stretch",
    "round",
    "round repeat",
    "round round",
    "round space",
    "round stretch",
    "space",
    "space repeat",
    "space round",
    "space space",
    "space stretch",
    "stretch",
    "stretch repeat",
    "stretch round",
    "stretch space",
    "stretch stretch",
]
_BorderImageSlice: TypeAlias = (
    _Quad[Percentage | float]
    | tuple[Literal["fill"] | Percentage | float, ...]
)
_BorderImageSource: TypeAlias = str
_BorderImageWidth: TypeAlias = _Quad[
    Length | Literal["auto"] | Percentage | float
]
_BorderInline: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderInlineColor: TypeAlias = _Pair[str]
_BorderInlineEnd: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderInlineEndColor: TypeAlias = str
_BorderInlineEndStyle: TypeAlias = _BorderBlockEndStyle
_BorderInlineEndWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderInlineStart: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderInlineStartColor: TypeAlias = str
_BorderInlineStartStyle: TypeAlias = _BorderBlockEndStyle
_BorderInlineStartWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderInlineStyle: TypeAlias = _BorderBlockStyle
_BorderInlineWidth: TypeAlias = _Pair[
    Length | Literal["medium", "thick", "thin"] | Literal[0]
]
_BorderLeft: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderLeftColor: TypeAlias = str
_BorderLeftStyle: TypeAlias = _BorderBlockEndStyle
_BorderLeftWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderRadius: TypeAlias = (
    _Quad[Length | Literal[0] | Percentage]
    | tuple[Length | Literal["/"] | Literal[0] | Percentage, ...]
)
_BorderRight: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderRightColor: TypeAlias = str
_BorderRightStyle: TypeAlias = _BorderBlockEndStyle
_BorderRightWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderShape: TypeAlias = (
    Literal["none"]
    | _Pair[
        RawCSS
        | tuple[
            Literal[
                "border-box",
                "content-box",
                "fill-box",
                "margin-box",
                "padding-box",
                "stroke-box",
                "view-box",
            ]
            | RawCSS,
            ...,
        ]
    ]
)
_BorderSpacing: TypeAlias = _Pair[Length | Literal[0]]
_BorderStartEndRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderStartStartRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderStyle: TypeAlias = _Quad[
    Literal[
        "dashed",
        "dotted",
        "double",
        "groove",
        "hidden",
        "inset",
        "none",
        "outset",
        "ridge",
        "solid",
    ]
]
_BorderTop: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_BorderTopColor: TypeAlias = str
_BorderTopLeftRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderTopRightRadius: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_BorderTopStyle: TypeAlias = _BorderBlockEndStyle
_BorderTopWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_BorderWidth: TypeAlias = _Quad[
    Length | Literal["medium", "thick", "thin"] | Literal[0]
]
_Bottom: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_BoxAlign: TypeAlias = Literal["baseline", "center", "end", "start", "stretch"]
_BoxDecorationBreak: TypeAlias = Literal["clone", "slice"]
_BoxDirection: TypeAlias = Literal["inherit", "normal", "reverse"]
_BoxFlex: TypeAlias = float
_BoxFlexGroup: TypeAlias = int
_BoxLines: TypeAlias = Literal["multiple", "single"]
_BoxOrdinalGroup: TypeAlias = int
_BoxOrient: TypeAlias = Literal[
    "block-axis", "horizontal", "inherit", "inline-axis", "vertical"
]
_BoxPack: TypeAlias = Literal["center", "end", "justify", "start"]
_BoxShadow: TypeAlias = (
    Literal["none"]
    | _Comma[
        tuple[Length | Literal[0] | str, ...]
        | tuple[
            Length | Literal[0],
            Length | Literal[0],
            Length | Literal[0],
            Length | Literal[0],
        ]
        | tuple[Length | Literal[0], Length | Literal[0], Length | Literal[0]]
        | tuple[Length | Literal[0], Length | Literal[0]]
    ]
)
_BoxSizing: TypeAlias = Literal["border-box", "content-box"]
_BreakAfter: TypeAlias = Literal[
    "all",
    "always",
    "auto",
    "avoid",
    "avoid-column",
    "avoid-page",
    "avoid-region",
    "column",
    "left",
    "page",
    "recto",
    "region",
    "right",
    "verso",
]
_BreakBefore: TypeAlias = _BreakAfter
_BreakInside: TypeAlias = Literal[
    "auto", "avoid", "avoid-column", "avoid-page", "avoid-region"
]
_CaptionSide: TypeAlias = Literal["bottom", "top"]
_Caret: TypeAlias = str | tuple[str, ...]
_CaretAnimation: TypeAlias = Literal["auto", "manual"]
_CaretColor: TypeAlias = str
_CaretShape: TypeAlias = Literal["auto", "bar", "block", "underscore"]
_Clear: TypeAlias = Literal[
    "both", "inline-end", "inline-start", "left", "none", "right"
]
_Clip: TypeAlias = Literal["auto"] | RawCSS
_ClipPath: TypeAlias = (
    RawCSS
    | str
    | tuple[
        Literal[
            "border-box",
            "content-box",
            "fill-box",
            "margin-box",
            "padding-box",
            "stroke-box",
            "view-box",
        ]
        | RawCSS,
        ...,
    ]
)
_ClipRule: TypeAlias = Literal["evenodd", "nonzero"]
_Color: TypeAlias = str
_ColorInterpolationFilters: TypeAlias = Literal["auto", "linearRGB", "sRGB"]
_ColorScheme: TypeAlias = Literal["normal"] | _Sequence[str] | tuple[str, ...]
_ColumnCount: TypeAlias = Literal["auto"] | int
_ColumnFill: TypeAlias = Literal["auto", "balance"]
_ColumnGap: TypeAlias = Length | Literal["normal"] | Literal[0] | Percentage
_ColumnHeight: TypeAlias = Length | Literal["auto"] | Literal[0]
_ColumnRule: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_ColumnRuleColor: TypeAlias = str
_ColumnRuleStyle: TypeAlias = _BorderBlockEndStyle
_ColumnRuleWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_ColumnSpan: TypeAlias = Literal["all", "none"]
_ColumnWidth: TypeAlias = Length | Literal["auto"] | Literal[0]
_ColumnWrap: TypeAlias = Literal["auto", "nowrap", "wrap"]
_Columns: TypeAlias = (
    Length
    | Literal["auto"]
    | int
    | tuple[Length | Literal["/", "auto"] | int, ...]
    | tuple[Length | Literal["auto"] | int, ...]
)
_Contain: TypeAlias = (
    Literal[
        "content",
        "inline-size",
        "inline-size size",
        "layout",
        "none",
        "paint",
        "size",
        "size inline-size",
        "strict",
        "style",
    ]
    | tuple[
        Literal[
            "inline-size",
            "inline-size size",
            "layout",
            "paint",
            "size",
            "size inline-size",
            "style",
        ],
        ...,
    ]
)
_ContainIntrinsicBlockSize: TypeAlias = (
    Length
    | Literal["none"]
    | Literal[0]
    | tuple[Length | Literal["auto", "none"] | Literal[0], ...]
)
_ContainIntrinsicHeight: TypeAlias = _ContainIntrinsicBlockSize
_ContainIntrinsicInlineSize: TypeAlias = _ContainIntrinsicBlockSize
_ContainIntrinsicSize: TypeAlias = _Pair[
    Length
    | Literal["none"]
    | Literal[0]
    | tuple[Length | Literal["auto", "none"] | Literal[0], ...]
]
_ContainIntrinsicWidth: TypeAlias = _ContainIntrinsicBlockSize
_Container: TypeAlias = Literal["none"] | _Sequence[str] | tuple[str, ...]
_ContainerName: TypeAlias = Literal["none"] | _Sequence[str]
_ContainerType: TypeAlias = Literal[
    "inline-size",
    "inline-size scroll-state",
    "normal",
    "scroll-state",
    "scroll-state inline-size",
    "scroll-state size",
    "size",
    "size scroll-state",
]
_Content: TypeAlias = _Sequence[RawCSS | str] | str | tuple[RawCSS | str, ...]
_ContentVisibility: TypeAlias = Literal["auto", "hidden", "visible"]
_CornerBlockEndShape: TypeAlias = _Pair[
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
]
_CornerBlockStartShape: TypeAlias = _CornerBlockEndShape
_CornerBottomLeftShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerBottomRightShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerBottomShape: TypeAlias = _CornerBlockEndShape
_CornerEndEndShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerEndStartShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerInlineEndShape: TypeAlias = _CornerBlockEndShape
_CornerInlineStartShape: TypeAlias = _CornerBlockEndShape
_CornerLeftShape: TypeAlias = _CornerBlockEndShape
_CornerRightShape: TypeAlias = _CornerBlockEndShape
_CornerShape: TypeAlias = _Quad[
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
]
_CornerStartEndShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerStartStartShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerTopLeftShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerTopRightShape: TypeAlias = (
    Literal["bevel", "notch", "round", "scoop", "square", "squircle"] | RawCSS
)
_CornerTopShape: TypeAlias = _CornerBlockEndShape
_CounterIncrement: TypeAlias = (
    Literal["none"] | _Sequence[str | tuple[int | str, ...]]
)
_CounterReset: TypeAlias = (
    Literal["none"]
    | _Sequence[
        RawCSS | str | tuple[RawCSS | int, ...] | tuple[int | str, ...]
    ]
)
_CounterSet: TypeAlias = (
    Literal["none"] | _Sequence[str | tuple[int | str, ...]]
)
_Cursor: TypeAlias = (
    Literal[
        "alias",
        "all-scroll",
        "auto",
        "cell",
        "col-resize",
        "context-menu",
        "copy",
        "crosshair",
        "default",
        "e-resize",
        "ew-resize",
        "grab",
        "grabbing",
        "help",
        "move",
        "n-resize",
        "ne-resize",
        "nesw-resize",
        "no-drop",
        "none",
        "not-allowed",
        "ns-resize",
        "nw-resize",
        "nwse-resize",
        "pointer",
        "progress",
        "row-resize",
        "s-resize",
        "se-resize",
        "sw-resize",
        "text",
        "vertical-text",
        "w-resize",
        "wait",
        "zoom-in",
        "zoom-out",
    ]
    | tuple[RawCSS | str, ...]
)
_Cx: TypeAlias = Length | Literal[0] | Percentage
_Cy: TypeAlias = Length | Literal[0] | Percentage
_D: TypeAlias = Literal["none"] | RawCSS
_DescentOverride: TypeAlias = Literal["normal"] | Percentage
_Direction: TypeAlias = Literal["ltr", "rtl"]
_Display: TypeAlias = Literal[
    "block",
    "block flex",
    "block flow",
    "block flow list-item",
    "block flow-root",
    "block flow-root list-item",
    "block grid",
    "block list-item",
    "block list-item flow",
    "block list-item flow-root",
    "block ruby",
    "block table",
    "contents",
    "flex",
    "flex block",
    "flex inline",
    "flex run-in",
    "flow",
    "flow block",
    "flow block list-item",
    "flow inline",
    "flow inline list-item",
    "flow list-item",
    "flow list-item block",
    "flow list-item inline",
    "flow list-item run-in",
    "flow run-in",
    "flow run-in list-item",
    "flow-root",
    "flow-root block",
    "flow-root block list-item",
    "flow-root inline",
    "flow-root inline list-item",
    "flow-root list-item",
    "flow-root list-item block",
    "flow-root list-item inline",
    "flow-root list-item run-in",
    "flow-root run-in",
    "flow-root run-in list-item",
    "grid",
    "grid block",
    "grid inline",
    "grid run-in",
    "inline",
    "inline flex",
    "inline flow",
    "inline flow list-item",
    "inline flow-root",
    "inline flow-root list-item",
    "inline grid",
    "inline list-item",
    "inline list-item flow",
    "inline list-item flow-root",
    "inline ruby",
    "inline table",
    "inline-block",
    "inline-flex",
    "inline-grid",
    "inline-list-item",
    "inline-table",
    "list-item",
    "list-item block",
    "list-item block flow",
    "list-item block flow-root",
    "list-item flow",
    "list-item flow block",
    "list-item flow inline",
    "list-item flow run-in",
    "list-item flow-root",
    "list-item flow-root block",
    "list-item flow-root inline",
    "list-item flow-root run-in",
    "list-item inline",
    "list-item inline flow",
    "list-item inline flow-root",
    "list-item run-in",
    "list-item run-in flow",
    "list-item run-in flow-root",
    "none",
    "ruby",
    "ruby block",
    "ruby inline",
    "ruby run-in",
    "ruby-base",
    "ruby-base-container",
    "ruby-text",
    "ruby-text-container",
    "run-in",
    "run-in flex",
    "run-in flow",
    "run-in flow list-item",
    "run-in flow-root",
    "run-in flow-root list-item",
    "run-in grid",
    "run-in list-item",
    "run-in list-item flow",
    "run-in list-item flow-root",
    "run-in ruby",
    "run-in table",
    "table",
    "table block",
    "table inline",
    "table run-in",
    "table-caption",
    "table-cell",
    "table-column",
    "table-column-group",
    "table-footer-group",
    "table-header-group",
    "table-row",
    "table-row-group",
]
_DominantBaseline: TypeAlias = Literal[
    "alphabetic",
    "auto",
    "central",
    "hanging",
    "ideographic",
    "mathematical",
    "middle",
    "text-bottom",
    "text-top",
]
_DynamicRangeLimit: TypeAlias = (
    Literal["constrained", "no-limit", "standard"] | RawCSS
)
_EmptyCells: TypeAlias = Literal["hide", "show"]
_Fallback: TypeAlias = str
_FieldSizing: TypeAlias = Literal["content", "fixed"]
_Fill: TypeAlias = str | tuple[str, ...]
_FillOpacity: TypeAlias = Percentage | float
_FillRule: TypeAlias = Literal["evenodd", "nonzero"]
_Filter: TypeAlias = Literal["none"] | _Sequence[RawCSS | str]
_Flex: TypeAlias = (
    Length
    | Literal[
        "auto", "content", "fit-content", "max-content", "min-content", "none"
    ]
    | Percentage
    | RawCSS
    | float
    | tuple[
        Length
        | Literal[
            "auto", "content", "fit-content", "max-content", "min-content"
        ]
        | Percentage
        | RawCSS
        | float,
        ...,
    ]
    | tuple[float, ...]
)
_FlexBasis: TypeAlias = (
    Length
    | Literal["auto", "content", "fit-content", "max-content", "min-content"]
    | Literal[0]
    | Percentage
    | RawCSS
)
_FlexDirection: TypeAlias = Literal[
    "column", "column-reverse", "row", "row-reverse"
]
_FlexFlow: TypeAlias = Literal[
    "balance",
    "balance column",
    "balance column-reverse",
    "balance row",
    "balance row-reverse",
    "balance wrap",
    "balance wrap column",
    "balance wrap column-reverse",
    "balance wrap row",
    "balance wrap row-reverse",
    "balance wrap-reverse",
    "balance wrap-reverse column",
    "balance wrap-reverse column-reverse",
    "balance wrap-reverse row",
    "balance wrap-reverse row-reverse",
    "column",
    "column balance",
    "column balance wrap",
    "column balance wrap-reverse",
    "column nowrap",
    "column wrap",
    "column wrap balance",
    "column wrap-reverse",
    "column wrap-reverse balance",
    "column-reverse",
    "column-reverse balance",
    "column-reverse balance wrap",
    "column-reverse balance wrap-reverse",
    "column-reverse nowrap",
    "column-reverse wrap",
    "column-reverse wrap balance",
    "column-reverse wrap-reverse",
    "column-reverse wrap-reverse balance",
    "nowrap",
    "nowrap column",
    "nowrap column-reverse",
    "nowrap row",
    "nowrap row-reverse",
    "row",
    "row balance",
    "row balance wrap",
    "row balance wrap-reverse",
    "row nowrap",
    "row wrap",
    "row wrap balance",
    "row wrap-reverse",
    "row wrap-reverse balance",
    "row-reverse",
    "row-reverse balance",
    "row-reverse balance wrap",
    "row-reverse balance wrap-reverse",
    "row-reverse nowrap",
    "row-reverse wrap",
    "row-reverse wrap balance",
    "row-reverse wrap-reverse",
    "row-reverse wrap-reverse balance",
    "wrap",
    "wrap balance",
    "wrap balance column",
    "wrap balance column-reverse",
    "wrap balance row",
    "wrap balance row-reverse",
    "wrap column",
    "wrap column-reverse",
    "wrap row",
    "wrap row-reverse",
    "wrap-reverse",
    "wrap-reverse balance",
    "wrap-reverse balance column",
    "wrap-reverse balance column-reverse",
    "wrap-reverse balance row",
    "wrap-reverse balance row-reverse",
    "wrap-reverse column",
    "wrap-reverse column-reverse",
    "wrap-reverse row",
    "wrap-reverse row-reverse",
]
_FlexGrow: TypeAlias = float
_FlexLineCount: TypeAlias = int
_FlexShrink: TypeAlias = float
_FlexWrap: TypeAlias = Literal[
    "balance",
    "balance wrap",
    "balance wrap-reverse",
    "nowrap",
    "wrap",
    "wrap balance",
    "wrap-reverse",
    "wrap-reverse balance",
]
_Float: TypeAlias = Literal[
    "inline-end", "inline-start", "left", "none", "right"
]
_FloodColor: TypeAlias = str
_FloodOpacity: TypeAlias = Percentage | float
_Font: TypeAlias = (
    Literal[
        "caption", "icon", "menu", "message-box", "small-caption", "status-bar"
    ]
    | tuple[Angle | Length | Percentage | float | str, ...]
)
_FontDisplay: TypeAlias = Literal[
    "auto", "block", "fallback", "optional", "swap"
]
_FontFamily: TypeAlias = _Comma[_Sequence[str] | str] | _Sequence[str] | str
_FontFeatureSettings: TypeAlias = (
    Literal["normal"] | _Comma[str | tuple[int | str, ...]]
)
_FontKerning: TypeAlias = Literal["auto", "none", "normal"]
_FontLanguageOverride: TypeAlias = str
_FontOpticalSizing: TypeAlias = Literal["auto", "none"]
_FontPalette: TypeAlias = RawCSS | str
_FontSize: TypeAlias = (
    Length
    | Literal[
        "large",
        "larger",
        "math",
        "medium",
        "small",
        "smaller",
        "x-large",
        "x-small",
        "xx-large",
        "xx-small",
        "xxx-large",
    ]
    | Literal[0]
    | Percentage
)
_FontSizeAdjust: TypeAlias = (
    Literal["from-font", "none"]
    | float
    | tuple[
        Literal[
            "cap-height",
            "ch-width",
            "ex-height",
            "from-font",
            "ic-height",
            "ic-width",
        ]
        | float,
        ...,
    ]
)
_FontSmooth: TypeAlias = (
    Length
    | Literal[
        "always",
        "auto",
        "large",
        "medium",
        "never",
        "small",
        "x-large",
        "x-small",
        "xx-large",
        "xx-small",
        "xxx-large",
    ]
    | Literal[0]
)
_FontStretch: TypeAlias = (
    Literal[
        "condensed",
        "expanded",
        "extra-condensed",
        "extra-expanded",
        "normal",
        "semi-condensed",
        "semi-expanded",
        "ultra-condensed",
        "ultra-expanded",
    ]
    | Percentage
    | _Pair[
        Literal[
            "condensed",
            "expanded",
            "extra-condensed",
            "extra-expanded",
            "normal",
            "semi-condensed",
            "semi-expanded",
            "ultra-condensed",
            "ultra-expanded",
        ]
        | Percentage
    ]
)
_FontStyle: TypeAlias = (
    Literal["italic", "normal", "oblique"]
    | tuple[Angle | Literal["oblique"] | Literal[0], ...]
)
_FontSynthesis: TypeAlias = Literal[
    "none",
    "position",
    "position small-caps",
    "position small-caps style",
    "position small-caps style weight",
    "position small-caps weight",
    "position small-caps weight style",
    "position style",
    "position style small-caps",
    "position style small-caps weight",
    "position style weight",
    "position style weight small-caps",
    "position weight",
    "position weight small-caps",
    "position weight small-caps style",
    "position weight style",
    "position weight style small-caps",
    "small-caps",
    "small-caps position",
    "small-caps position style",
    "small-caps position style weight",
    "small-caps position weight",
    "small-caps position weight style",
    "small-caps style",
    "small-caps style position",
    "small-caps style position weight",
    "small-caps style weight",
    "small-caps style weight position",
    "small-caps weight",
    "small-caps weight position",
    "small-caps weight position style",
    "small-caps weight style",
    "small-caps weight style position",
    "style",
    "style position",
    "style position small-caps",
    "style position small-caps weight",
    "style position weight",
    "style position weight small-caps",
    "style small-caps",
    "style small-caps position",
    "style small-caps position weight",
    "style small-caps weight",
    "style small-caps weight position",
    "style weight",
    "style weight position",
    "style weight position small-caps",
    "style weight small-caps",
    "style weight small-caps position",
    "weight",
    "weight position",
    "weight position small-caps",
    "weight position small-caps style",
    "weight position style",
    "weight position style small-caps",
    "weight small-caps",
    "weight small-caps position",
    "weight small-caps position style",
    "weight small-caps style",
    "weight small-caps style position",
    "weight style",
    "weight style position",
    "weight style position small-caps",
    "weight style small-caps",
    "weight style small-caps position",
]
_FontSynthesisPosition: TypeAlias = Literal["auto", "none"]
_FontSynthesisSmallCaps: TypeAlias = Literal["auto", "none"]
_FontSynthesisStyle: TypeAlias = Literal["auto", "none"]
_FontSynthesisWeight: TypeAlias = Literal["auto", "none"]
_FontVariant: TypeAlias = (
    Literal[
        "all-petite-caps",
        "all-small-caps",
        "common-ligatures",
        "contextual",
        "diagonal-fractions",
        "discretionary-ligatures",
        "full-width",
        "historical-forms",
        "historical-ligatures",
        "jis04",
        "jis78",
        "jis83",
        "jis90",
        "lining-nums",
        "no-common-ligatures",
        "no-contextual",
        "no-discretionary-ligatures",
        "no-historical-ligatures",
        "none",
        "normal",
        "oldstyle-nums",
        "ordinal",
        "petite-caps",
        "proportional-nums",
        "proportional-width",
        "ruby",
        "simplified",
        "slashed-zero",
        "small-caps",
        "stacked-fractions",
        "tabular-nums",
        "titling-caps",
        "traditional",
        "unicase",
    ]
    | RawCSS
    | tuple[
        Literal[
            "all-petite-caps",
            "all-small-caps",
            "common-ligatures",
            "contextual",
            "diagonal-fractions",
            "discretionary-ligatures",
            "full-width",
            "historical-forms",
            "historical-ligatures",
            "jis04",
            "jis78",
            "jis83",
            "jis90",
            "lining-nums",
            "no-common-ligatures",
            "no-contextual",
            "no-discretionary-ligatures",
            "no-historical-ligatures",
            "oldstyle-nums",
            "ordinal",
            "petite-caps",
            "proportional-nums",
            "proportional-width",
            "ruby",
            "simplified",
            "slashed-zero",
            "small-caps",
            "stacked-fractions",
            "tabular-nums",
            "titling-caps",
            "traditional",
            "unicase",
        ]
        | RawCSS,
        ...,
    ]
)
_FontVariantAlternates: TypeAlias = (
    Literal["historical-forms", "normal"]
    | RawCSS
    | tuple[Literal["historical-forms"] | RawCSS, ...]
)
_FontVariantCaps: TypeAlias = Literal[
    "all-petite-caps",
    "all-small-caps",
    "normal",
    "petite-caps",
    "small-caps",
    "titling-caps",
    "unicase",
]
_FontVariantEastAsian: TypeAlias = Literal[
    "full-width",
    "full-width jis04",
    "full-width jis04 ruby",
    "full-width jis78",
    "full-width jis78 ruby",
    "full-width jis83",
    "full-width jis83 ruby",
    "full-width jis90",
    "full-width jis90 ruby",
    "full-width ruby",
    "full-width ruby jis04",
    "full-width ruby jis78",
    "full-width ruby jis83",
    "full-width ruby jis90",
    "full-width ruby simplified",
    "full-width ruby traditional",
    "full-width simplified",
    "full-width simplified ruby",
    "full-width traditional",
    "full-width traditional ruby",
    "jis04",
    "jis04 full-width",
    "jis04 full-width ruby",
    "jis04 proportional-width",
    "jis04 proportional-width ruby",
    "jis04 ruby",
    "jis04 ruby full-width",
    "jis04 ruby proportional-width",
    "jis78",
    "jis78 full-width",
    "jis78 full-width ruby",
    "jis78 proportional-width",
    "jis78 proportional-width ruby",
    "jis78 ruby",
    "jis78 ruby full-width",
    "jis78 ruby proportional-width",
    "jis83",
    "jis83 full-width",
    "jis83 full-width ruby",
    "jis83 proportional-width",
    "jis83 proportional-width ruby",
    "jis83 ruby",
    "jis83 ruby full-width",
    "jis83 ruby proportional-width",
    "jis90",
    "jis90 full-width",
    "jis90 full-width ruby",
    "jis90 proportional-width",
    "jis90 proportional-width ruby",
    "jis90 ruby",
    "jis90 ruby full-width",
    "jis90 ruby proportional-width",
    "normal",
    "proportional-width",
    "proportional-width jis04",
    "proportional-width jis04 ruby",
    "proportional-width jis78",
    "proportional-width jis78 ruby",
    "proportional-width jis83",
    "proportional-width jis83 ruby",
    "proportional-width jis90",
    "proportional-width jis90 ruby",
    "proportional-width ruby",
    "proportional-width ruby jis04",
    "proportional-width ruby jis78",
    "proportional-width ruby jis83",
    "proportional-width ruby jis90",
    "proportional-width ruby simplified",
    "proportional-width ruby traditional",
    "proportional-width simplified",
    "proportional-width simplified ruby",
    "proportional-width traditional",
    "proportional-width traditional ruby",
    "ruby",
    "ruby full-width",
    "ruby full-width jis04",
    "ruby full-width jis78",
    "ruby full-width jis83",
    "ruby full-width jis90",
    "ruby full-width simplified",
    "ruby full-width traditional",
    "ruby jis04",
    "ruby jis04 full-width",
    "ruby jis04 proportional-width",
    "ruby jis78",
    "ruby jis78 full-width",
    "ruby jis78 proportional-width",
    "ruby jis83",
    "ruby jis83 full-width",
    "ruby jis83 proportional-width",
    "ruby jis90",
    "ruby jis90 full-width",
    "ruby jis90 proportional-width",
    "ruby proportional-width",
    "ruby proportional-width jis04",
    "ruby proportional-width jis78",
    "ruby proportional-width jis83",
    "ruby proportional-width jis90",
    "ruby proportional-width simplified",
    "ruby proportional-width traditional",
    "ruby simplified",
    "ruby simplified full-width",
    "ruby simplified proportional-width",
    "ruby traditional",
    "ruby traditional full-width",
    "ruby traditional proportional-width",
    "simplified",
    "simplified full-width",
    "simplified full-width ruby",
    "simplified proportional-width",
    "simplified proportional-width ruby",
    "simplified ruby",
    "simplified ruby full-width",
    "simplified ruby proportional-width",
    "traditional",
    "traditional full-width",
    "traditional full-width ruby",
    "traditional proportional-width",
    "traditional proportional-width ruby",
    "traditional ruby",
    "traditional ruby full-width",
    "traditional ruby proportional-width",
]
_FontVariantEmoji: TypeAlias = Literal["emoji", "normal", "text", "unicode"]
_FontVariantLigatures: TypeAlias = (
    Literal[
        "common-ligatures",
        "contextual",
        "discretionary-ligatures",
        "historical-ligatures",
        "no-common-ligatures",
        "no-contextual",
        "no-discretionary-ligatures",
        "no-historical-ligatures",
        "none",
        "normal",
    ]
    | tuple[
        Literal[
            "common-ligatures",
            "contextual",
            "discretionary-ligatures",
            "historical-ligatures",
            "no-common-ligatures",
            "no-contextual",
            "no-discretionary-ligatures",
            "no-historical-ligatures",
        ],
        ...,
    ]
)
_FontVariantNumeric: TypeAlias = (
    Literal[
        "diagonal-fractions",
        "lining-nums",
        "normal",
        "oldstyle-nums",
        "ordinal",
        "proportional-nums",
        "slashed-zero",
        "stacked-fractions",
        "tabular-nums",
    ]
    | tuple[
        Literal[
            "diagonal-fractions",
            "lining-nums",
            "oldstyle-nums",
            "ordinal",
            "proportional-nums",
            "slashed-zero",
            "stacked-fractions",
            "tabular-nums",
        ],
        ...,
    ]
)
_FontVariantPosition: TypeAlias = Literal["normal", "sub", "super"]
_FontVariationSettings: TypeAlias = (
    Literal["normal"] | _Comma[tuple[float | str, ...]]
)
_FontWeight: TypeAlias = (
    Literal["bold", "bolder", "lighter", "normal"]
    | _Pair[Literal["bold", "normal"] | float]
    | float
)
_FontWidth: TypeAlias = (
    Literal[
        "condensed",
        "expanded",
        "extra-condensed",
        "extra-expanded",
        "normal",
        "semi-condensed",
        "semi-expanded",
        "ultra-condensed",
        "ultra-expanded",
    ]
    | Percentage
)
_ForcedColorAdjust: TypeAlias = Literal[
    "auto", "none", "preserve-parent-color"
]
_FrameSizing: TypeAlias = Literal[
    "auto",
    "content-block-size",
    "content-height",
    "content-inline-size",
    "content-width",
]
_Gap: TypeAlias = (
    Length
    | Literal["normal"]
    | Literal[0]
    | Percentage
    | tuple[Length | Literal["normal"] | Literal[0] | Percentage, ...]
)
_Grid: TypeAlias = (
    Literal["none"]
    | _Sequence[
        str
        | tuple[
            Fractions | Length | Literal[0] | Percentage | RawCSS | str, ...
        ]
    ]
    | tuple[Fractions | Length | Literal[0] | Percentage | RawCSS | str, ...]
)
_GridArea: TypeAlias = int | str | tuple[int | str, ...]
_GridAutoColumns: TypeAlias = _Sequence[
    Fractions
    | Length
    | Literal["auto", "max-content", "min-content"]
    | Literal[0]
    | Percentage
    | RawCSS
]
_GridAutoFlow: TypeAlias = Literal[
    "column",
    "column dense",
    "dense",
    "dense column",
    "dense row",
    "row",
    "row dense",
]
_GridAutoRows: TypeAlias = _GridAutoColumns
_GridColumn: TypeAlias = int | str | tuple[int | str, ...]
_GridColumnEnd: TypeAlias = int | str | tuple[int | str, ...]
_GridColumnGap: TypeAlias = Length | Literal[0] | Percentage
_GridColumnStart: TypeAlias = int | str | tuple[int | str, ...]
_GridGap: TypeAlias = (
    Length
    | Literal[0]
    | Percentage
    | tuple[Length | Literal[0] | Percentage, ...]
)
_GridRow: TypeAlias = int | str | tuple[int | str, ...]
_GridRowEnd: TypeAlias = int | str | tuple[int | str, ...]
_GridRowGap: TypeAlias = Length | Literal[0] | Percentage
_GridRowStart: TypeAlias = int | str | tuple[int | str, ...]
_GridTemplate: TypeAlias = _Grid
_GridTemplateAreas: TypeAlias = Literal["none"] | _Sequence[str]
_GridTemplateColumns: TypeAlias = (
    Literal["none", "subgrid"]
    | RawCSS
    | _Sequence[
        Fractions
        | Length
        | Literal["auto", "max-content", "min-content"]
        | Literal[0]
        | Percentage
        | RawCSS
        | tuple[
            Fractions | Length | Literal[0] | Percentage | RawCSS | str, ...
        ]
    ]
    | tuple[Fractions | Length | Literal[0] | Percentage | RawCSS | str, ...]
    | tuple[Length | Literal[0] | Percentage | RawCSS | str, ...]
    | tuple[RawCSS | str, ...]
)
_GridTemplateRows: TypeAlias = _GridTemplateColumns
_HangingPunctuation: TypeAlias = Literal[
    "allow-end",
    "allow-end first",
    "allow-end first last",
    "allow-end last",
    "allow-end last first",
    "first",
    "first allow-end",
    "first allow-end last",
    "first force-end",
    "first force-end last",
    "first last",
    "first last allow-end",
    "first last force-end",
    "force-end",
    "force-end first",
    "force-end first last",
    "force-end last",
    "force-end last first",
    "last",
    "last allow-end",
    "last allow-end first",
    "last first",
    "last first allow-end",
    "last first force-end",
    "last force-end",
    "last force-end first",
    "none",
]
_Height: TypeAlias = _BlockSize
_HyphenateCharacter: TypeAlias = str
_HyphenateLimitChars: TypeAlias = _Triple[Literal["auto"] | int]
_Hyphens: TypeAlias = Literal["auto", "manual", "none"]
_ImageOrientation: TypeAlias = (
    Angle
    | Literal["flip", "from-image"]
    | Literal[0]
    | tuple[Angle | Literal["flip"] | Literal[0], ...]
)
_ImageRendering: TypeAlias = Literal[
    "auto", "crisp-edges", "pixelated", "smooth"
]
_ImageResolution: TypeAlias = (
    Literal["from-image"]
    | Resolution
    | tuple[Literal["from-image", "snap"] | Resolution, ...]
    | tuple[Literal["from-image"] | Resolution, ...]
)
_ImeMode: TypeAlias = Literal[
    "active", "auto", "disabled", "inactive", "normal"
]
_Inherits: TypeAlias = Literal["false", "true"]
_InitialLetter: TypeAlias = Literal["normal"] | float | tuple[float, ...]
_InitialLetterAlign: TypeAlias = Literal[
    "alphabetic", "auto", "hanging", "ideographic"
]
_InitialValue: TypeAlias = (
    Angle
    | Fractions
    | Frequency
    | Length
    | Percentage
    | Resolution
    | Time
    | float
    | str
)
_InlineSize: TypeAlias = _BlockSize
_Inset: TypeAlias = _Quad[
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
]
_InsetBlock: TypeAlias = _Pair[
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
]
_InsetBlockEnd: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_InsetBlockStart: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_InsetInline: TypeAlias = _Pair[
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
]
_InsetInlineEnd: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_InsetInlineStart: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_Interactivity: TypeAlias = Literal["auto", "inert"]
_InterestDelay: TypeAlias = _Pair[Literal["normal"] | Time]
_InterestDelayEnd: TypeAlias = Literal["normal"] | Time
_InterestDelayStart: TypeAlias = Literal["normal"] | Time
_InterpolateSize: TypeAlias = Literal["allow-keywords", "numeric-only"]
_Isolation: TypeAlias = Literal["auto", "isolate"]
_JustifyContent: TypeAlias = Literal[
    "center",
    "end",
    "flex-end",
    "flex-start",
    "left",
    "normal",
    "right",
    "safe center",
    "safe end",
    "safe flex-end",
    "safe flex-start",
    "safe left",
    "safe right",
    "safe start",
    "space-around",
    "space-between",
    "space-evenly",
    "start",
    "stretch",
    "unsafe center",
    "unsafe end",
    "unsafe flex-end",
    "unsafe flex-start",
    "unsafe left",
    "unsafe right",
    "unsafe start",
]
_JustifyItems: TypeAlias = Literal[
    "anchor-center",
    "baseline",
    "center",
    "center legacy",
    "end",
    "first baseline",
    "flex-end",
    "flex-start",
    "last baseline",
    "left",
    "left legacy",
    "legacy",
    "legacy center",
    "legacy left",
    "legacy right",
    "normal",
    "right",
    "right legacy",
    "safe center",
    "safe end",
    "safe flex-end",
    "safe flex-start",
    "safe left",
    "safe right",
    "safe self-end",
    "safe self-start",
    "safe start",
    "self-end",
    "self-start",
    "start",
    "stretch",
    "unsafe center",
    "unsafe end",
    "unsafe flex-end",
    "unsafe flex-start",
    "unsafe left",
    "unsafe right",
    "unsafe self-end",
    "unsafe self-start",
    "unsafe start",
]
_JustifySelf: TypeAlias = Literal[
    "anchor-center",
    "auto",
    "baseline",
    "center",
    "end",
    "first baseline",
    "flex-end",
    "flex-start",
    "last baseline",
    "left",
    "normal",
    "right",
    "safe center",
    "safe end",
    "safe flex-end",
    "safe flex-start",
    "safe left",
    "safe right",
    "safe self-end",
    "safe self-start",
    "safe start",
    "self-end",
    "self-start",
    "start",
    "stretch",
    "unsafe center",
    "unsafe end",
    "unsafe flex-end",
    "unsafe flex-start",
    "unsafe left",
    "unsafe right",
    "unsafe self-end",
    "unsafe self-start",
    "unsafe start",
]
_JustifyTracks: TypeAlias = _Comma[
    Literal[
        "center",
        "end",
        "flex-end",
        "flex-start",
        "left",
        "normal",
        "right",
        "safe center",
        "safe end",
        "safe flex-end",
        "safe flex-start",
        "safe left",
        "safe right",
        "safe start",
        "space-around",
        "space-between",
        "space-evenly",
        "start",
        "stretch",
        "unsafe center",
        "unsafe end",
        "unsafe flex-end",
        "unsafe flex-start",
        "unsafe left",
        "unsafe right",
        "unsafe start",
    ]
]
_Left: TypeAlias = Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
_LetterSpacing: TypeAlias = Length | Literal["normal"] | Literal[0]
_LightingColor: TypeAlias = str
_LineBreak: TypeAlias = Literal[
    "anywhere", "auto", "loose", "normal", "strict"
]
_LineClamp: TypeAlias = Literal["none"] | int
_LineGapOverride: TypeAlias = Literal["normal"] | Percentage
_LineHeight: TypeAlias = Length | Literal["normal"] | Percentage | float
_LineHeightStep: TypeAlias = Length | Literal[0]
_LinkParameters: TypeAlias = Literal["none"] | _Comma[RawCSS]
_ListStyle: TypeAlias = RawCSS | str | tuple[RawCSS | str, ...]
_ListStyleImage: TypeAlias = str
_ListStylePosition: TypeAlias = Literal["inside", "outside"]
_ListStyleType: TypeAlias = RawCSS | str
_Margin: TypeAlias = _Quad[
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
]
_MarginBlock: TypeAlias = _Pair[
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
]
_MarginBlockEnd: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginBlockStart: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginBottom: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginInline: TypeAlias = _Pair[
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
]
_MarginInlineEnd: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginInlineStart: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginLeft: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginRight: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginTop: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
)
_MarginTrim: TypeAlias = Literal["all", "in-flow", "none"]
_Marker: TypeAlias = str
_MarkerEnd: TypeAlias = str
_MarkerMid: TypeAlias = str
_MarkerStart: TypeAlias = str
_Marks: TypeAlias = Literal[
    "crop", "crop cross", "cross", "cross crop", "none"
]
_Mask: TypeAlias = _Comma[
    Length
    | Literal[0]
    | Percentage
    | str
    | tuple[
        Length
        | Literal[
            "/",
            "auto",
            "bottom",
            "bottom center",
            "bottom left",
            "bottom right",
            "center",
            "center bottom",
            "center center",
            "center left",
            "center right",
            "center top",
            "contain",
            "cover",
            "left",
            "left bottom",
            "left center",
            "left top",
            "right",
            "right bottom",
            "right center",
            "right top",
            "top",
            "top center",
            "top left",
            "top right",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[Length | Literal[0] | Percentage | str, ...]
]
_MaskBorder: TypeAlias = _BorderImage
_MaskBorderMode: TypeAlias = Literal["alpha", "luminance"]
_MaskBorderOutset: TypeAlias = _Quad[Length | float]
_MaskBorderRepeat: TypeAlias = _BorderImageRepeat
_MaskBorderSlice: TypeAlias = (
    _Quad[Percentage | float]
    | tuple[Literal["fill"] | Percentage | float, ...]
)
_MaskBorderSource: TypeAlias = str
_MaskBorderWidth: TypeAlias = _Quad[
    Length | Literal["auto"] | Percentage | float
]
_MaskClip: TypeAlias = _Comma[
    Literal[
        "border-box",
        "content-box",
        "fill-box",
        "no-clip",
        "padding-box",
        "stroke-box",
        "view-box",
    ]
]
_MaskComposite: TypeAlias = _Comma[
    Literal["add", "exclude", "intersect", "subtract"]
]
_MaskImage: TypeAlias = _Comma[str]
_MaskMode: TypeAlias = _Comma[Literal["alpha", "luminance", "match-source"]]
_MaskOrigin: TypeAlias = _Comma[
    Literal[
        "border-box",
        "content-box",
        "fill-box",
        "padding-box",
        "stroke-box",
        "view-box",
    ]
]
_MaskPosition: TypeAlias = _Comma[
    Length
    | Literal[
        "bottom",
        "bottom center",
        "bottom left",
        "bottom right",
        "center",
        "center bottom",
        "center center",
        "center left",
        "center right",
        "center top",
        "left",
        "left bottom",
        "left center",
        "left top",
        "right",
        "right bottom",
        "right center",
        "right top",
        "top",
        "top center",
        "top left",
        "top right",
    ]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_MaskRepeat: TypeAlias = _BackgroundRepeat
_MaskSize: TypeAlias = _BackgroundSize
_MaskType: TypeAlias = Literal["alpha", "luminance"]
_MasonryAutoFlow: TypeAlias = Literal[
    "definite-first",
    "definite-first next",
    "definite-first pack",
    "next",
    "next definite-first",
    "next ordered",
    "ordered",
    "ordered next",
    "ordered pack",
    "pack",
    "pack definite-first",
    "pack ordered",
]
_MathDepth: TypeAlias = Literal["auto-add"] | RawCSS | int
_MathShift: TypeAlias = Literal["compact", "normal"]
_MathStyle: TypeAlias = Literal["compact", "normal"]
_MaxBlockSize: TypeAlias = (
    Length
    | Literal["fit-content", "max-content", "min-content", "none"]
    | Literal[0]
    | Percentage
    | RawCSS
)
_MaxHeight: TypeAlias = _MaxBlockSize
_MaxInlineSize: TypeAlias = _MaxBlockSize
_MaxLines: TypeAlias = Literal["none"] | int
_MaxWidth: TypeAlias = _MaxBlockSize
_MinBlockSize: TypeAlias = _BlockSize
_MinHeight: TypeAlias = _BlockSize
_MinInlineSize: TypeAlias = _BlockSize
_MinWidth: TypeAlias = _BlockSize
_MixBlendMode: TypeAlias = Literal[
    "color",
    "color-burn",
    "color-dodge",
    "darken",
    "difference",
    "exclusion",
    "hard-light",
    "hue",
    "lighten",
    "luminosity",
    "multiply",
    "normal",
    "overlay",
    "plus-darker",
    "plus-lighter",
    "saturation",
    "screen",
    "soft-light",
]
_Navigation: TypeAlias = Literal["auto", "none"]
_Negative: TypeAlias = str | tuple[str, ...]
_ObjectFit: TypeAlias = Literal[
    "contain", "cover", "fill", "none", "scale-down"
]
_ObjectPosition: TypeAlias = (
    Length
    | Literal[
        "bottom",
        "bottom center",
        "bottom left",
        "bottom right",
        "center",
        "center bottom",
        "center center",
        "center left",
        "center right",
        "center top",
        "left",
        "left bottom",
        "left center",
        "left top",
        "right",
        "right bottom",
        "right center",
        "right top",
        "top",
        "top center",
        "top left",
        "top right",
    ]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
)
_ObjectViewBox: TypeAlias = Literal["none"] | RawCSS
_Offset: TypeAlias = (
    Length
    | Literal[0]
    | Percentage
    | RawCSS
    | str
    | tuple[Angle | Length | Literal[0] | Percentage | RawCSS | str, ...]
    | tuple[
        Length
        | Literal[
            "/",
            "auto",
            "bottom",
            "bottom center",
            "bottom left",
            "bottom right",
            "center",
            "center bottom",
            "center center",
            "center left",
            "center right",
            "center top",
            "left",
            "left bottom",
            "left center",
            "left top",
            "right",
            "right bottom",
            "right center",
            "right top",
            "top",
            "top center",
            "top left",
            "top right",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[RawCSS | str, ...]
)
_OffsetAnchor: TypeAlias = (
    Length
    | Literal[
        "auto",
        "bottom",
        "bottom center",
        "bottom left",
        "bottom right",
        "center",
        "center bottom",
        "center center",
        "center left",
        "center right",
        "center top",
        "left",
        "left bottom",
        "left center",
        "left top",
        "right",
        "right bottom",
        "right center",
        "right top",
        "top",
        "top center",
        "top left",
        "top right",
    ]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
)
_OffsetDistance: TypeAlias = Length | Literal[0] | Percentage
_OffsetPath: TypeAlias = RawCSS | str | tuple[RawCSS | str, ...]
_OffsetPosition: TypeAlias = (
    Length
    | Literal[
        "auto",
        "bottom",
        "bottom center",
        "bottom left",
        "bottom right",
        "center",
        "center bottom",
        "center center",
        "center left",
        "center right",
        "center top",
        "left",
        "left bottom",
        "left center",
        "left top",
        "normal",
        "right",
        "right bottom",
        "right center",
        "right top",
        "top",
        "top center",
        "top left",
        "top right",
    ]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
    | tuple[
        Length
        | Literal["bottom", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
)
_OffsetRotate: TypeAlias = (
    Angle
    | Literal["auto", "reverse"]
    | Literal[0]
    | tuple[Angle | Literal["auto", "reverse"] | Literal[0], ...]
)
_Opacity: TypeAlias = Percentage | float
_Order: TypeAlias = int
_Orphans: TypeAlias = int
_Outline: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_OutlineColor: TypeAlias = str
_OutlineOffset: TypeAlias = Length | Literal[0]
_OutlineStyle: TypeAlias = Literal[
    "auto",
    "dashed",
    "dotted",
    "double",
    "groove",
    "inset",
    "none",
    "outset",
    "ridge",
    "solid",
]
_OutlineWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_Overflow: TypeAlias = Literal[
    "auto",
    "auto auto",
    "auto clip",
    "auto hidden",
    "auto scroll",
    "auto visible",
    "clip",
    "clip auto",
    "clip clip",
    "clip hidden",
    "clip scroll",
    "clip visible",
    "hidden",
    "hidden auto",
    "hidden clip",
    "hidden hidden",
    "hidden scroll",
    "hidden visible",
    "scroll",
    "scroll auto",
    "scroll clip",
    "scroll hidden",
    "scroll scroll",
    "scroll visible",
    "visible",
    "visible auto",
    "visible clip",
    "visible hidden",
    "visible scroll",
    "visible visible",
]
_OverflowAnchor: TypeAlias = Literal["auto", "none"]
_OverflowBlock: TypeAlias = Literal[
    "auto", "clip", "hidden", "scroll", "visible"
]
_OverflowClipBox: TypeAlias = Literal["content-box", "padding-box"]
_OverflowClipMargin: TypeAlias = (
    Length
    | Literal["border-box", "content-box", "padding-box"]
    | Literal[0]
    | tuple[
        Length
        | Literal["border-box", "content-box", "padding-box"]
        | Literal[0],
        ...,
    ]
)
_OverflowInline: TypeAlias = Literal[
    "auto", "clip", "hidden", "scroll", "visible"
]
_OverflowWrap: TypeAlias = Literal["anywhere", "break-word", "normal"]
_OverflowX: TypeAlias = Literal["auto", "clip", "hidden", "scroll", "visible"]
_OverflowY: TypeAlias = Literal["auto", "clip", "hidden", "scroll", "visible"]
_Overlay: TypeAlias = Literal["auto", "none"]
_OverrideColors: TypeAlias = _Comma[tuple[int | str, ...]]
_OverscrollBehavior: TypeAlias = Literal[
    "auto",
    "auto auto",
    "auto contain",
    "auto none",
    "contain",
    "contain auto",
    "contain contain",
    "contain none",
    "none",
    "none auto",
    "none contain",
    "none none",
]
_OverscrollBehaviorBlock: TypeAlias = Literal["auto", "contain", "none"]
_OverscrollBehaviorInline: TypeAlias = Literal["auto", "contain", "none"]
_OverscrollBehaviorX: TypeAlias = Literal["auto", "contain", "none"]
_OverscrollBehaviorY: TypeAlias = Literal["auto", "contain", "none"]
_Pad: TypeAlias = tuple[int | str, ...]
_Padding: TypeAlias = _Quad[Length | Literal[0] | Percentage]
_PaddingBlock: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_PaddingBlockEnd: TypeAlias = Length | Literal[0] | Percentage
_PaddingBlockStart: TypeAlias = Length | Literal[0] | Percentage
_PaddingBottom: TypeAlias = Length | Literal[0] | Percentage
_PaddingInline: TypeAlias = _Pair[Length | Literal[0] | Percentage]
_PaddingInlineEnd: TypeAlias = Length | Literal[0] | Percentage
_PaddingInlineStart: TypeAlias = Length | Literal[0] | Percentage
_PaddingLeft: TypeAlias = Length | Literal[0] | Percentage
_PaddingRight: TypeAlias = Length | Literal[0] | Percentage
_PaddingTop: TypeAlias = Length | Literal[0] | Percentage
_Page: TypeAlias = str
_PageBreakAfter: TypeAlias = Literal[
    "always", "auto", "avoid", "left", "recto", "right", "verso"
]
_PageBreakBefore: TypeAlias = Literal[
    "always", "auto", "avoid", "left", "recto", "right", "verso"
]
_PageBreakInside: TypeAlias = Literal["auto", "avoid"]
_PageMarginSafety: TypeAlias = Literal["add", "clamp", "none"]
_PageOrientation: TypeAlias = Literal["rotate-left", "rotate-right", "upright"]
_PaintOrder: TypeAlias = Literal[
    "fill",
    "fill markers",
    "fill markers stroke",
    "fill stroke",
    "fill stroke markers",
    "markers",
    "markers fill",
    "markers fill stroke",
    "markers stroke",
    "markers stroke fill",
    "normal",
    "stroke",
    "stroke fill",
    "stroke fill markers",
    "stroke markers",
    "stroke markers fill",
]
_PathLength: TypeAlias = (
    Literal["none"] | tuple[Length | Literal[",", "∞"] | Literal[0], ...]
)
_Perspective: TypeAlias = Length | Literal["none"] | Literal[0]
_PerspectiveOrigin: TypeAlias = _ObjectPosition
_PlaceContent: TypeAlias = (
    Literal[
        "baseline",
        "center",
        "end",
        "first baseline",
        "flex-end",
        "flex-start",
        "last baseline",
        "normal",
        "safe center",
        "safe end",
        "safe flex-end",
        "safe flex-start",
        "safe start",
        "space-around",
        "space-between",
        "space-evenly",
        "start",
        "stretch",
        "unsafe center",
        "unsafe end",
        "unsafe flex-end",
        "unsafe flex-start",
        "unsafe start",
    ]
    | tuple[
        Literal[
            "baseline",
            "center",
            "end",
            "first baseline",
            "flex-end",
            "flex-start",
            "last baseline",
            "left",
            "normal",
            "right",
            "safe center",
            "safe end",
            "safe flex-end",
            "safe flex-start",
            "safe left",
            "safe right",
            "safe start",
            "space-around",
            "space-between",
            "space-evenly",
            "start",
            "stretch",
            "unsafe center",
            "unsafe end",
            "unsafe flex-end",
            "unsafe flex-start",
            "unsafe left",
            "unsafe right",
            "unsafe start",
        ],
        ...,
    ]
)
_PlaceItems: TypeAlias = (
    Literal[
        "anchor-center",
        "baseline",
        "center",
        "end",
        "first baseline",
        "flex-end",
        "flex-start",
        "last baseline",
        "normal",
        "safe center",
        "safe end",
        "safe flex-end",
        "safe flex-start",
        "safe self-end",
        "safe self-start",
        "safe start",
        "self-end",
        "self-start",
        "start",
        "stretch",
        "unsafe center",
        "unsafe end",
        "unsafe flex-end",
        "unsafe flex-start",
        "unsafe self-end",
        "unsafe self-start",
        "unsafe start",
    ]
    | tuple[
        Literal[
            "anchor-center",
            "baseline",
            "center",
            "center legacy",
            "end",
            "first baseline",
            "flex-end",
            "flex-start",
            "last baseline",
            "left",
            "left legacy",
            "legacy",
            "legacy center",
            "legacy left",
            "legacy right",
            "normal",
            "right",
            "right legacy",
            "safe center",
            "safe end",
            "safe flex-end",
            "safe flex-start",
            "safe left",
            "safe right",
            "safe self-end",
            "safe self-start",
            "safe start",
            "self-end",
            "self-start",
            "start",
            "stretch",
            "unsafe center",
            "unsafe end",
            "unsafe flex-end",
            "unsafe flex-start",
            "unsafe left",
            "unsafe right",
            "unsafe self-end",
            "unsafe self-start",
            "unsafe start",
        ],
        ...,
    ]
)
_PlaceSelf: TypeAlias = (
    Literal[
        "anchor-center",
        "auto",
        "baseline",
        "center",
        "end",
        "first baseline",
        "flex-end",
        "flex-start",
        "last baseline",
        "normal",
        "safe center",
        "safe end",
        "safe flex-end",
        "safe flex-start",
        "safe self-end",
        "safe self-start",
        "safe start",
        "self-end",
        "self-start",
        "start",
        "stretch",
        "unsafe center",
        "unsafe end",
        "unsafe flex-end",
        "unsafe flex-start",
        "unsafe self-end",
        "unsafe self-start",
        "unsafe start",
    ]
    | tuple[
        Literal[
            "anchor-center",
            "auto",
            "baseline",
            "center",
            "end",
            "first baseline",
            "flex-end",
            "flex-start",
            "last baseline",
            "left",
            "normal",
            "right",
            "safe center",
            "safe end",
            "safe flex-end",
            "safe flex-start",
            "safe left",
            "safe right",
            "safe self-end",
            "safe self-start",
            "safe start",
            "self-end",
            "self-start",
            "start",
            "stretch",
            "unsafe center",
            "unsafe end",
            "unsafe flex-end",
            "unsafe flex-start",
            "unsafe left",
            "unsafe right",
            "unsafe self-end",
            "unsafe self-start",
            "unsafe start",
        ],
        ...,
    ]
)
_PointerEvents: TypeAlias = Literal[
    "all",
    "auto",
    "fill",
    "inherit",
    "none",
    "painted",
    "stroke",
    "visible",
    "visibleFill",
    "visiblePainted",
    "visibleStroke",
]
_Position: TypeAlias = Literal[
    "absolute", "fixed", "relative", "static", "sticky"
]
_PositionAnchor: TypeAlias = str
_PositionArea: TypeAlias = (
    Literal[
        "block-end",
        "block-end center",
        "block-end inline-end",
        "block-end inline-start",
        "block-end span-all",
        "block-end span-inline-end",
        "block-end span-inline-start",
        "block-start",
        "block-start center",
        "block-start inline-end",
        "block-start inline-start",
        "block-start span-all",
        "block-start span-inline-end",
        "block-start span-inline-start",
        "bottom",
        "center",
        "center block-end",
        "center block-start",
        "center center",
        "center end",
        "center inline-end",
        "center inline-start",
        "center self-block-end",
        "center self-block-start",
        "center self-end",
        "center self-inline-end",
        "center self-inline-start",
        "center self-start",
        "center span-all",
        "center span-block-end",
        "center span-block-start",
        "center span-end",
        "center span-inline-end",
        "center span-inline-start",
        "center span-self-block-end",
        "center span-self-block-start",
        "center span-self-end",
        "center span-self-inline-end",
        "center span-self-inline-start",
        "center span-self-start",
        "center span-start",
        "center start",
        "end",
        "end center",
        "end end",
        "end span-all",
        "end span-end",
        "end span-start",
        "end start",
        "inline-end",
        "inline-end block-end",
        "inline-end block-start",
        "inline-end center",
        "inline-end span-all",
        "inline-end span-block-end",
        "inline-end span-block-start",
        "inline-start",
        "inline-start block-end",
        "inline-start block-start",
        "inline-start center",
        "inline-start span-all",
        "inline-start span-block-end",
        "inline-start span-block-start",
        "left",
        "none",
        "right",
        "self-block-end",
        "self-block-end center",
        "self-block-end self-inline-end",
        "self-block-end self-inline-start",
        "self-block-end span-all",
        "self-block-end span-self-inline-end",
        "self-block-end span-self-inline-start",
        "self-block-start",
        "self-block-start center",
        "self-block-start self-inline-end",
        "self-block-start self-inline-start",
        "self-block-start span-all",
        "self-block-start span-self-inline-end",
        "self-block-start span-self-inline-start",
        "self-end",
        "self-end center",
        "self-end self-end",
        "self-end self-start",
        "self-end span-all",
        "self-end span-self-end",
        "self-end span-self-start",
        "self-inline-end",
        "self-inline-end center",
        "self-inline-end self-block-end",
        "self-inline-end self-block-start",
        "self-inline-end span-all",
        "self-inline-end span-self-block-end",
        "self-inline-end span-self-block-start",
        "self-inline-start",
        "self-inline-start center",
        "self-inline-start self-block-end",
        "self-inline-start self-block-start",
        "self-inline-start span-all",
        "self-inline-start span-self-block-end",
        "self-inline-start span-self-block-start",
        "self-start",
        "self-start center",
        "self-start self-end",
        "self-start self-start",
        "self-start span-all",
        "self-start span-self-end",
        "self-start span-self-start",
        "span-all",
        "span-all block-end",
        "span-all block-start",
        "span-all center",
        "span-all end",
        "span-all inline-end",
        "span-all inline-start",
        "span-all self-block-end",
        "span-all self-block-start",
        "span-all self-end",
        "span-all self-inline-end",
        "span-all self-inline-start",
        "span-all self-start",
        "span-all span-all",
        "span-all span-block-end",
        "span-all span-block-start",
        "span-all span-end",
        "span-all span-inline-end",
        "span-all span-inline-start",
        "span-all span-self-block-end",
        "span-all span-self-block-start",
        "span-all span-self-end",
        "span-all span-self-inline-end",
        "span-all span-self-inline-start",
        "span-all span-self-start",
        "span-all span-start",
        "span-all start",
        "span-block-end",
        "span-block-end center",
        "span-block-end inline-end",
        "span-block-end inline-start",
        "span-block-end span-all",
        "span-block-end span-inline-end",
        "span-block-end span-inline-start",
        "span-block-start",
        "span-block-start center",
        "span-block-start inline-end",
        "span-block-start inline-start",
        "span-block-start span-all",
        "span-block-start span-inline-end",
        "span-block-start span-inline-start",
        "span-bottom",
        "span-end",
        "span-end center",
        "span-end end",
        "span-end span-all",
        "span-end span-end",
        "span-end span-start",
        "span-end start",
        "span-inline-end",
        "span-inline-end block-end",
        "span-inline-end block-start",
        "span-inline-end center",
        "span-inline-end span-all",
        "span-inline-end span-block-end",
        "span-inline-end span-block-start",
        "span-inline-start",
        "span-inline-start block-end",
        "span-inline-start block-start",
        "span-inline-start center",
        "span-inline-start span-all",
        "span-inline-start span-block-end",
        "span-inline-start span-block-start",
        "span-left",
        "span-right",
        "span-self-block-end",
        "span-self-block-end center",
        "span-self-block-end self-inline-end",
        "span-self-block-end self-inline-start",
        "span-self-block-end span-all",
        "span-self-block-end span-self-inline-end",
        "span-self-block-end span-self-inline-start",
        "span-self-block-start",
        "span-self-block-start center",
        "span-self-block-start self-inline-end",
        "span-self-block-start self-inline-start",
        "span-self-block-start span-all",
        "span-self-block-start span-self-inline-end",
        "span-self-block-start span-self-inline-start",
        "span-self-end",
        "span-self-end center",
        "span-self-end self-end",
        "span-self-end self-start",
        "span-self-end span-all",
        "span-self-end span-self-end",
        "span-self-end span-self-start",
        "span-self-inline-end",
        "span-self-inline-end center",
        "span-self-inline-end self-block-end",
        "span-self-inline-end self-block-start",
        "span-self-inline-end span-all",
        "span-self-inline-end span-self-block-end",
        "span-self-inline-end span-self-block-start",
        "span-self-inline-start",
        "span-self-inline-start center",
        "span-self-inline-start self-block-end",
        "span-self-inline-start self-block-start",
        "span-self-inline-start span-all",
        "span-self-inline-start span-self-block-end",
        "span-self-inline-start span-self-block-start",
        "span-self-start",
        "span-self-start center",
        "span-self-start self-end",
        "span-self-start self-start",
        "span-self-start span-all",
        "span-self-start span-self-end",
        "span-self-start span-self-start",
        "span-start",
        "span-start center",
        "span-start end",
        "span-start span-all",
        "span-start span-end",
        "span-start span-start",
        "span-start start",
        "span-top",
        "span-x-end",
        "span-x-self-end",
        "span-x-self-start",
        "span-x-start",
        "span-y-end",
        "span-y-self-end",
        "span-y-self-start",
        "span-y-start",
        "start",
        "start center",
        "start end",
        "start span-all",
        "start span-end",
        "start span-start",
        "start start",
        "top",
        "x-end",
        "x-self-end",
        "x-self-start",
        "x-start",
        "y-end",
        "y-self-end",
        "y-self-start",
        "y-start",
    ]
    | tuple[
        Literal[
            "bottom",
            "center",
            "left",
            "right",
            "span-all",
            "span-bottom",
            "span-left",
            "span-right",
            "span-top",
            "span-x-end",
            "span-x-self-end",
            "span-x-self-start",
            "span-x-start",
            "span-y-end",
            "span-y-self-end",
            "span-y-self-start",
            "span-y-start",
            "top",
            "x-end",
            "x-self-end",
            "x-self-start",
            "x-start",
            "y-end",
            "y-self-end",
            "y-self-start",
            "y-start",
        ],
        ...,
    ]
)
_PositionTry: TypeAlias = (
    Literal["none"]
    | _Comma[
        str
        | tuple[
            Literal[
                "bottom",
                "center",
                "left",
                "right",
                "span-all",
                "span-bottom",
                "span-left",
                "span-right",
                "span-top",
                "span-x-end",
                "span-x-self-end",
                "span-x-self-start",
                "span-x-start",
                "span-y-end",
                "span-y-self-end",
                "span-y-self-start",
                "span-y-start",
                "top",
                "x-end",
                "x-self-end",
                "x-self-start",
                "x-start",
                "y-end",
                "y-self-end",
                "y-self-start",
                "y-start",
            ],
            ...,
        ]
        | tuple[str, ...]
    ]
    | tuple[str, ...]
)
_PositionTryFallbacks: TypeAlias = (
    Literal["none"]
    | _Comma[
        str
        | tuple[
            Literal[
                "bottom",
                "center",
                "left",
                "right",
                "span-all",
                "span-bottom",
                "span-left",
                "span-right",
                "span-top",
                "span-x-end",
                "span-x-self-end",
                "span-x-self-start",
                "span-x-start",
                "span-y-end",
                "span-y-self-end",
                "span-y-self-start",
                "span-y-start",
                "top",
                "x-end",
                "x-self-end",
                "x-self-start",
                "x-start",
                "y-end",
                "y-self-end",
                "y-self-start",
                "y-start",
            ],
            ...,
        ]
        | tuple[str, ...]
    ]
)
_PositionTryOrder: TypeAlias = Literal[
    "most-block-size",
    "most-height",
    "most-inline-size",
    "most-width",
    "normal",
]
_PositionVisibility: TypeAlias = Literal[
    "always",
    "anchors-valid",
    "anchors-valid anchors-visible",
    "anchors-valid anchors-visible no-overflow",
    "anchors-valid no-overflow",
    "anchors-valid no-overflow anchors-visible",
    "anchors-visible",
    "anchors-visible anchors-valid",
    "anchors-visible anchors-valid no-overflow",
    "anchors-visible no-overflow",
    "anchors-visible no-overflow anchors-valid",
    "no-overflow",
    "no-overflow anchors-valid",
    "no-overflow anchors-valid anchors-visible",
    "no-overflow anchors-visible",
    "no-overflow anchors-visible anchors-valid",
]
_Prefix: TypeAlias = str
_PrintColorAdjust: TypeAlias = Literal["economy", "exact"]
_Quotes: TypeAlias = Literal["auto", "none"] | _Sequence[tuple[str, ...]]
_R: TypeAlias = Length | Literal[0] | Percentage
_Range: TypeAlias = (
    Literal["auto"]
    | _Comma[tuple[Literal["infinite"] | int, Literal["infinite"] | int]]
)
_ReadingFlow: TypeAlias = Literal[
    "flex-flow",
    "flex-visual",
    "grid-columns",
    "grid-order",
    "grid-rows",
    "normal",
    "source-order",
]
_ReadingOrder: TypeAlias = int
_Resize: TypeAlias = Literal[
    "block", "both", "horizontal", "inline", "none", "vertical"
]
_Right: TypeAlias = Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
_Rotate: TypeAlias = (
    Angle
    | Literal["none"]
    | Literal[0]
    | tuple[Angle | Literal["x", "y", "z"] | float, ...]
)
_RowGap: TypeAlias = Length | Literal["normal"] | Literal[0] | Percentage
_RubyAlign: TypeAlias = Literal[
    "center", "space-around", "space-between", "start"
]
_RubyMerge: TypeAlias = Literal["auto", "collapse", "separate"]
_RubyOverhang: TypeAlias = Literal["auto", "none"]
_RubyPosition: TypeAlias = Literal[
    "alternate",
    "alternate over",
    "alternate under",
    "inter-character",
    "over",
    "over alternate",
    "under",
    "under alternate",
]
_Rx: TypeAlias = Length | Literal["auto"] | Literal[0] | Percentage
_Ry: TypeAlias = Length | Literal["auto"] | Literal[0] | Percentage
_Scale: TypeAlias = Literal["none"] | _Triple[Percentage | float]
_ScrollAxisLock: TypeAlias = Literal["auto", "none"]
_ScrollBehavior: TypeAlias = Literal["auto", "smooth"]
_ScrollInitialTarget: TypeAlias = Literal["nearest", "none"]
_ScrollMargin: TypeAlias = _Quad[Length | Literal[0]]
_ScrollMarginBlock: TypeAlias = _Pair[Length | Literal[0]]
_ScrollMarginBlockEnd: TypeAlias = Length | Literal[0]
_ScrollMarginBlockStart: TypeAlias = Length | Literal[0]
_ScrollMarginBottom: TypeAlias = Length | Literal[0]
_ScrollMarginInline: TypeAlias = _Pair[Length | Literal[0]]
_ScrollMarginInlineEnd: TypeAlias = Length | Literal[0]
_ScrollMarginInlineStart: TypeAlias = Length | Literal[0]
_ScrollMarginLeft: TypeAlias = Length | Literal[0]
_ScrollMarginRight: TypeAlias = Length | Literal[0]
_ScrollMarginTop: TypeAlias = Length | Literal[0]
_ScrollMarkerGroup: TypeAlias = Literal["after", "before", "none"]
_ScrollPadding: TypeAlias = _Quad[
    Length | Literal["auto"] | Literal[0] | Percentage
]
_ScrollPaddingBlock: TypeAlias = _Pair[
    Length | Literal["auto"] | Literal[0] | Percentage
]
_ScrollPaddingBlockEnd: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingBlockStart: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingBottom: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingInline: TypeAlias = _Pair[
    Length | Literal["auto"] | Literal[0] | Percentage
]
_ScrollPaddingInlineEnd: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingInlineStart: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingLeft: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingRight: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollPaddingTop: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_ScrollSnapAlign: TypeAlias = Literal[
    "center",
    "center center",
    "center end",
    "center none",
    "center start",
    "end",
    "end center",
    "end end",
    "end none",
    "end start",
    "none",
    "none center",
    "none end",
    "none none",
    "none start",
    "start",
    "start center",
    "start end",
    "start none",
    "start start",
]
_ScrollSnapCoordinate: TypeAlias = (
    Literal["none"]
    | _Comma[
        Length
        | Literal[
            "bottom",
            "bottom center",
            "bottom left",
            "bottom right",
            "center",
            "center bottom",
            "center center",
            "center left",
            "center right",
            "center top",
            "left",
            "left bottom",
            "left center",
            "left top",
            "right",
            "right bottom",
            "right center",
            "right top",
            "top",
            "top center",
            "top left",
            "top right",
        ]
        | Literal[0]
        | Percentage
        | tuple[
            Length
            | Literal["bottom", "center", "left", "right", "top"]
            | Literal[0]
            | Percentage,
            ...,
        ]
        | tuple[
            Length
            | Literal["bottom", "left", "right", "top"]
            | Literal[0]
            | Percentage,
            ...,
        ]
    ]
)
_ScrollSnapDestination: TypeAlias = _ObjectPosition
_ScrollSnapPointsX: TypeAlias = Literal["none"] | RawCSS
_ScrollSnapPointsY: TypeAlias = Literal["none"] | RawCSS
_ScrollSnapStop: TypeAlias = Literal["always", "normal"]
_ScrollSnapType: TypeAlias = Literal[
    "block",
    "block mandatory",
    "block proximity",
    "both",
    "both mandatory",
    "both proximity",
    "inline",
    "inline mandatory",
    "inline proximity",
    "none",
    "x",
    "x mandatory",
    "x proximity",
    "y",
    "y mandatory",
    "y proximity",
]
_ScrollSnapTypeX: TypeAlias = Literal["mandatory", "none", "proximity"]
_ScrollSnapTypeY: TypeAlias = Literal["mandatory", "none", "proximity"]
_ScrollTargetGroup: TypeAlias = Literal["auto", "none"]
_ScrollTimeline: TypeAlias = _Comma[_Comma[str] | tuple[str, ...]]
_ScrollTimelineAxis: TypeAlias = _Comma[Literal["block", "inline", "x", "y"]]
_ScrollTimelineName: TypeAlias = _Comma[str]
_ScrollbarColor: TypeAlias = Literal["auto"] | tuple[str, str]
_ScrollbarGutter: TypeAlias = Literal[
    "auto", "both-edges stable", "stable", "stable both-edges"
]
_ScrollbarWidth: TypeAlias = Literal["auto", "none", "thin"]
_ShapeImageThreshold: TypeAlias = Percentage | float
_ShapeMargin: TypeAlias = Length | Literal[0] | Percentage
_ShapeOutside: TypeAlias = (
    RawCSS
    | str
    | tuple[
        Literal["border-box", "content-box", "margin-box", "padding-box"]
        | RawCSS,
        ...,
    ]
)
_ShapeRendering: TypeAlias = Literal[
    "auto", "crispEdges", "geometricPrecision", "optimizeSpeed"
]
_Size: TypeAlias = (
    Literal[
        "A3",
        "A3 landscape",
        "A3 portrait",
        "A4",
        "A4 landscape",
        "A4 portrait",
        "A5",
        "A5 landscape",
        "A5 portrait",
        "B4",
        "B4 landscape",
        "B4 portrait",
        "B5",
        "B5 landscape",
        "B5 portrait",
        "JIS-B4",
        "JIS-B4 landscape",
        "JIS-B4 portrait",
        "JIS-B5",
        "JIS-B5 landscape",
        "JIS-B5 portrait",
        "auto",
        "landscape",
        "landscape A3",
        "landscape A4",
        "landscape A5",
        "landscape B4",
        "landscape B5",
        "landscape JIS-B4",
        "landscape JIS-B5",
        "landscape ledger",
        "landscape legal",
        "landscape letter",
        "ledger",
        "ledger landscape",
        "ledger portrait",
        "legal",
        "legal landscape",
        "legal portrait",
        "letter",
        "letter landscape",
        "letter portrait",
        "portrait",
        "portrait A3",
        "portrait A4",
        "portrait A5",
        "portrait B4",
        "portrait B5",
        "portrait JIS-B4",
        "portrait JIS-B5",
        "portrait ledger",
        "portrait legal",
        "portrait letter",
    ]
    | _Pair[Length | Literal[0]]
)
_SizeAdjust: TypeAlias = Percentage
_SpeakAs: TypeAlias = str
_Src: TypeAlias = _Comma[RawCSS | str | tuple[RawCSS | str, ...]]
_StopColor: TypeAlias = str
_StopOpacity: TypeAlias = Percentage | float
_Stroke: TypeAlias = str | tuple[str, ...]
_StrokeColor: TypeAlias = str
_StrokeDasharray: TypeAlias = (
    Literal["none"] | _Comma[_Sequence[Length | Percentage | float]]
)
_StrokeDashoffset: TypeAlias = Length | Percentage | float
_StrokeLinecap: TypeAlias = Literal["butt", "round", "square"]
_StrokeLinejoin: TypeAlias = Literal[
    "arcs", "bevel", "miter", "miter-clip", "round"
]
_StrokeMiterlimit: TypeAlias = float
_StrokeOpacity: TypeAlias = Percentage | float
_StrokeWidth: TypeAlias = Length | Percentage | float
_Suffix: TypeAlias = str
_Symbols: TypeAlias = _Sequence[str]
_Syntax: TypeAlias = str
_System: TypeAlias = (
    Literal["additive", "alphabetic", "cyclic", "fixed", "numeric", "symbolic"]
    | tuple[Literal["fixed"] | int, ...]
    | tuple[str, ...]
)
_TabSize: TypeAlias = Length | int
_TableLayout: TypeAlias = Literal["auto", "fixed"]
_TextAlign: TypeAlias = Literal[
    "center", "end", "justify", "left", "match-parent", "right", "start"
]
_TextAlignLast: TypeAlias = Literal[
    "auto", "center", "end", "justify", "left", "right", "start"
]
_TextAnchor: TypeAlias = Literal["end", "middle", "start"]
_TextAutospace: TypeAlias = Literal["auto", "normal"] | RawCSS
_TextBox: TypeAlias = (
    Literal[
        "auto",
        "cap",
        "cap alphabetic",
        "cap ideographic",
        "cap ideographic-ink",
        "cap text",
        "ex",
        "ex alphabetic",
        "ex ideographic",
        "ex ideographic-ink",
        "ex text",
        "ideographic",
        "ideographic alphabetic",
        "ideographic ideographic",
        "ideographic ideographic-ink",
        "ideographic text",
        "ideographic-ink",
        "ideographic-ink alphabetic",
        "ideographic-ink ideographic",
        "ideographic-ink ideographic-ink",
        "ideographic-ink text",
        "none",
        "normal",
        "text",
        "text alphabetic",
        "text ideographic",
        "text ideographic-ink",
        "text text",
        "trim-both",
        "trim-end",
        "trim-start",
    ]
    | tuple[
        Literal[
            "auto",
            "cap",
            "cap alphabetic",
            "cap ideographic",
            "cap ideographic-ink",
            "cap text",
            "ex",
            "ex alphabetic",
            "ex ideographic",
            "ex ideographic-ink",
            "ex text",
            "ideographic",
            "ideographic alphabetic",
            "ideographic ideographic",
            "ideographic ideographic-ink",
            "ideographic text",
            "ideographic-ink",
            "ideographic-ink alphabetic",
            "ideographic-ink ideographic",
            "ideographic-ink ideographic-ink",
            "ideographic-ink text",
            "none",
            "text",
            "text alphabetic",
            "text ideographic",
            "text ideographic-ink",
            "text text",
            "trim-both",
            "trim-end",
            "trim-start",
        ],
        ...,
    ]
)
_TextBoxEdge: TypeAlias = Literal[
    "auto",
    "cap",
    "cap alphabetic",
    "cap ideographic",
    "cap ideographic-ink",
    "cap text",
    "ex",
    "ex alphabetic",
    "ex ideographic",
    "ex ideographic-ink",
    "ex text",
    "ideographic",
    "ideographic alphabetic",
    "ideographic ideographic",
    "ideographic ideographic-ink",
    "ideographic text",
    "ideographic-ink",
    "ideographic-ink alphabetic",
    "ideographic-ink ideographic",
    "ideographic-ink ideographic-ink",
    "ideographic-ink text",
    "text",
    "text alphabetic",
    "text ideographic",
    "text ideographic-ink",
    "text text",
]
_TextBoxTrim: TypeAlias = Literal[
    "none", "trim-both", "trim-end", "trim-start"
]
_TextCombineUpright: TypeAlias = (
    Literal["all", "digits", "none"] | tuple[Literal["digits"] | int, ...]
)
_TextDecoration: TypeAlias = (
    Length
    | Literal[0]
    | Percentage
    | str
    | tuple[Length | Literal[0] | Percentage | str, ...]
)
_TextDecorationColor: TypeAlias = str
_TextDecorationInset: TypeAlias = (
    Literal["auto"] | _Pair[Length | Literal[0] | Percentage]
)
_TextDecorationLine: TypeAlias = Literal[
    "blink",
    "blink line-through",
    "blink line-through overline",
    "blink line-through overline underline",
    "blink line-through underline",
    "blink line-through underline overline",
    "blink overline",
    "blink overline line-through",
    "blink overline line-through underline",
    "blink overline underline",
    "blink overline underline line-through",
    "blink underline",
    "blink underline line-through",
    "blink underline line-through overline",
    "blink underline overline",
    "blink underline overline line-through",
    "grammar-error",
    "line-through",
    "line-through blink",
    "line-through blink overline",
    "line-through blink overline underline",
    "line-through blink underline",
    "line-through blink underline overline",
    "line-through overline",
    "line-through overline blink",
    "line-through overline blink underline",
    "line-through overline underline",
    "line-through overline underline blink",
    "line-through underline",
    "line-through underline blink",
    "line-through underline blink overline",
    "line-through underline overline",
    "line-through underline overline blink",
    "none",
    "overline",
    "overline blink",
    "overline blink line-through",
    "overline blink line-through underline",
    "overline blink underline",
    "overline blink underline line-through",
    "overline line-through",
    "overline line-through blink",
    "overline line-through blink underline",
    "overline line-through underline",
    "overline line-through underline blink",
    "overline underline",
    "overline underline blink",
    "overline underline blink line-through",
    "overline underline line-through",
    "overline underline line-through blink",
    "spelling-error",
    "underline",
    "underline blink",
    "underline blink line-through",
    "underline blink line-through overline",
    "underline blink overline",
    "underline blink overline line-through",
    "underline line-through",
    "underline line-through blink",
    "underline line-through blink overline",
    "underline line-through overline",
    "underline line-through overline blink",
    "underline overline",
    "underline overline blink",
    "underline overline blink line-through",
    "underline overline line-through",
    "underline overline line-through blink",
]
_TextDecorationSkip: TypeAlias = (
    Literal[
        "box-decoration",
        "edges",
        "leading-spaces",
        "leading-spaces trailing-spaces",
        "none",
        "objects",
        "spaces",
        "trailing-spaces",
        "trailing-spaces leading-spaces",
    ]
    | tuple[
        Literal[
            "box-decoration",
            "edges",
            "leading-spaces",
            "leading-spaces trailing-spaces",
            "objects",
            "spaces",
            "trailing-spaces",
            "trailing-spaces leading-spaces",
        ],
        ...,
    ]
)
_TextDecorationSkipInk: TypeAlias = Literal["all", "auto", "none"]
_TextDecorationStyle: TypeAlias = Literal[
    "dashed", "dotted", "double", "solid", "wavy"
]
_TextDecorationThickness: TypeAlias = (
    Length | Literal["auto", "from-font"] | Literal[0] | Percentage
)
_TextEmphasis: TypeAlias = str | tuple[str, ...]
_TextEmphasisColor: TypeAlias = str
_TextEmphasisPosition: TypeAlias = Literal[
    "auto",
    "left over",
    "left under",
    "over",
    "over left",
    "over right",
    "right over",
    "right under",
    "under",
    "under left",
    "under right",
]
_TextEmphasisStyle: TypeAlias = str
_TextFit: TypeAlias = (
    Literal["grow", "none", "shrink"]
    | tuple[
        Literal[
            "consistent", "grow", "none", "per-line", "per-line-all", "shrink"
        ]
        | Percentage,
        ...,
    ]
)
_TextIndent: TypeAlias = (
    Length
    | Literal[0]
    | Percentage
    | tuple[
        Length | Literal["each-line", "hanging"] | Literal[0] | Percentage, ...
    ]
)
_TextJustify: TypeAlias = Literal[
    "auto", "inter-character", "inter-word", "none"
]
_TextOrientation: TypeAlias = Literal["mixed", "sideways", "upright"]
_TextOverflow: TypeAlias = _Pair[str]
_TextRendering: TypeAlias = Literal[
    "auto", "geometricPrecision", "optimizeLegibility", "optimizeSpeed"
]
_TextShadow: TypeAlias = (
    Literal["none"]
    | _Comma[
        tuple[Length | Literal[0] | str, ...]
        | tuple[Length | Literal[0], Length | Literal[0], Length | Literal[0]]
        | tuple[Length | Literal[0], Length | Literal[0]]
    ]
)
_TextSizeAdjust: TypeAlias = Literal["auto", "none"] | Percentage
_TextSpacingTrim: TypeAlias = Literal[
    "normal", "space-all", "space-first", "trim-start"
]
_TextTransform: TypeAlias = Literal[
    "capitalize",
    "capitalize full-size-kana",
    "capitalize full-size-kana full-width",
    "capitalize full-width",
    "capitalize full-width full-size-kana",
    "full-size-kana",
    "full-size-kana capitalize",
    "full-size-kana capitalize full-width",
    "full-size-kana full-width",
    "full-size-kana full-width capitalize",
    "full-size-kana full-width lowercase",
    "full-size-kana full-width uppercase",
    "full-size-kana lowercase",
    "full-size-kana lowercase full-width",
    "full-size-kana uppercase",
    "full-size-kana uppercase full-width",
    "full-width",
    "full-width capitalize",
    "full-width capitalize full-size-kana",
    "full-width full-size-kana",
    "full-width full-size-kana capitalize",
    "full-width full-size-kana lowercase",
    "full-width full-size-kana uppercase",
    "full-width lowercase",
    "full-width lowercase full-size-kana",
    "full-width uppercase",
    "full-width uppercase full-size-kana",
    "lowercase",
    "lowercase full-size-kana",
    "lowercase full-size-kana full-width",
    "lowercase full-width",
    "lowercase full-width full-size-kana",
    "math-auto",
    "none",
    "uppercase",
    "uppercase full-size-kana",
    "uppercase full-size-kana full-width",
    "uppercase full-width",
    "uppercase full-width full-size-kana",
]
_TextUnderlineOffset: TypeAlias = (
    Length | Literal["auto"] | Literal[0] | Percentage
)
_TextUnderlinePosition: TypeAlias = Literal[
    "auto",
    "from-font",
    "left",
    "left under",
    "right",
    "right under",
    "under",
    "under left",
    "under right",
]
_TextWrap: TypeAlias = Literal[
    "auto",
    "auto nowrap",
    "auto wrap",
    "balance",
    "balance nowrap",
    "balance wrap",
    "nowrap",
    "nowrap auto",
    "nowrap balance",
    "nowrap pretty",
    "nowrap stable",
    "pretty",
    "pretty nowrap",
    "pretty wrap",
    "stable",
    "stable nowrap",
    "stable wrap",
    "wrap",
    "wrap auto",
    "wrap balance",
    "wrap pretty",
    "wrap stable",
]
_TextWrapMode: TypeAlias = Literal["nowrap", "wrap"]
_TextWrapStyle: TypeAlias = Literal["auto", "balance", "pretty", "stable"]
_TimelineScope: TypeAlias = Literal["none"] | _Comma[str]
_TimelineTrigger: TypeAlias = (
    Literal["none"]
    | _Comma[tuple[Length | Literal[0] | Percentage | RawCSS | str, ...]]
)
_TimelineTriggerActivationRange: TypeAlias = _AnimationRange
_TimelineTriggerActivationRangeEnd: TypeAlias = _AnimationRangeEnd
_TimelineTriggerActivationRangeStart: TypeAlias = _AnimationRangeEnd
_TimelineTriggerActiveRange: TypeAlias = _Comma[
    _Comma[
        Length
        | Literal[
            "auto",
            "contain",
            "cover",
            "entry",
            "entry-crossing",
            "exit",
            "exit-crossing",
            "normal",
        ]
        | Literal[0]
        | Percentage
        | tuple[
            Length
            | Literal[
                "contain",
                "cover",
                "entry",
                "entry-crossing",
                "exit",
                "exit-crossing",
            ]
            | Literal[0]
            | Percentage,
            ...,
        ]
    ]
    | tuple[
        Length
        | Literal[
            "auto",
            "contain",
            "cover",
            "entry",
            "entry-crossing",
            "exit",
            "exit-crossing",
            "normal",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_TimelineTriggerActiveRangeEnd: TypeAlias = _Comma[
    Length
    | Literal[
        "auto",
        "contain",
        "cover",
        "entry",
        "entry-crossing",
        "exit",
        "exit-crossing",
        "normal",
    ]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal[
            "contain",
            "cover",
            "entry",
            "entry-crossing",
            "exit",
            "exit-crossing",
        ]
        | Literal[0]
        | Percentage,
        ...,
    ]
]
_TimelineTriggerActiveRangeStart: TypeAlias = _TimelineTriggerActiveRangeEnd
_TimelineTriggerName: TypeAlias = Literal["none"] | _Comma[str]
_TimelineTriggerSource: TypeAlias = _Comma[RawCSS | str]
_Top: TypeAlias = Length | Literal["auto"] | Literal[0] | Percentage | RawCSS
_TouchAction: TypeAlias = Literal[
    "auto",
    "manipulation",
    "none",
    "pan-down",
    "pan-down pan-left",
    "pan-down pan-left pinch-zoom",
    "pan-down pan-right",
    "pan-down pan-right pinch-zoom",
    "pan-down pan-x",
    "pan-down pan-x pinch-zoom",
    "pan-down pinch-zoom",
    "pan-down pinch-zoom pan-left",
    "pan-down pinch-zoom pan-right",
    "pan-down pinch-zoom pan-x",
    "pan-left",
    "pan-left pan-down",
    "pan-left pan-down pinch-zoom",
    "pan-left pan-up",
    "pan-left pan-up pinch-zoom",
    "pan-left pan-y",
    "pan-left pan-y pinch-zoom",
    "pan-left pinch-zoom",
    "pan-left pinch-zoom pan-down",
    "pan-left pinch-zoom pan-up",
    "pan-left pinch-zoom pan-y",
    "pan-right",
    "pan-right pan-down",
    "pan-right pan-down pinch-zoom",
    "pan-right pan-up",
    "pan-right pan-up pinch-zoom",
    "pan-right pan-y",
    "pan-right pan-y pinch-zoom",
    "pan-right pinch-zoom",
    "pan-right pinch-zoom pan-down",
    "pan-right pinch-zoom pan-up",
    "pan-right pinch-zoom pan-y",
    "pan-up",
    "pan-up pan-left",
    "pan-up pan-left pinch-zoom",
    "pan-up pan-right",
    "pan-up pan-right pinch-zoom",
    "pan-up pan-x",
    "pan-up pan-x pinch-zoom",
    "pan-up pinch-zoom",
    "pan-up pinch-zoom pan-left",
    "pan-up pinch-zoom pan-right",
    "pan-up pinch-zoom pan-x",
    "pan-x",
    "pan-x pan-down",
    "pan-x pan-down pinch-zoom",
    "pan-x pan-up",
    "pan-x pan-up pinch-zoom",
    "pan-x pan-y",
    "pan-x pan-y pinch-zoom",
    "pan-x pinch-zoom",
    "pan-x pinch-zoom pan-down",
    "pan-x pinch-zoom pan-up",
    "pan-x pinch-zoom pan-y",
    "pan-y",
    "pan-y pan-left",
    "pan-y pan-left pinch-zoom",
    "pan-y pan-right",
    "pan-y pan-right pinch-zoom",
    "pan-y pan-x",
    "pan-y pan-x pinch-zoom",
    "pan-y pinch-zoom",
    "pan-y pinch-zoom pan-left",
    "pan-y pinch-zoom pan-right",
    "pan-y pinch-zoom pan-x",
    "pinch-zoom",
    "pinch-zoom pan-down",
    "pinch-zoom pan-down pan-left",
    "pinch-zoom pan-down pan-right",
    "pinch-zoom pan-down pan-x",
    "pinch-zoom pan-left",
    "pinch-zoom pan-left pan-down",
    "pinch-zoom pan-left pan-up",
    "pinch-zoom pan-left pan-y",
    "pinch-zoom pan-right",
    "pinch-zoom pan-right pan-down",
    "pinch-zoom pan-right pan-up",
    "pinch-zoom pan-right pan-y",
    "pinch-zoom pan-up",
    "pinch-zoom pan-up pan-left",
    "pinch-zoom pan-up pan-right",
    "pinch-zoom pan-up pan-x",
    "pinch-zoom pan-x",
    "pinch-zoom pan-x pan-down",
    "pinch-zoom pan-x pan-up",
    "pinch-zoom pan-x pan-y",
    "pinch-zoom pan-y",
    "pinch-zoom pan-y pan-left",
    "pinch-zoom pan-y pan-right",
    "pinch-zoom pan-y pan-x",
]
_Transform: TypeAlias = Literal["none"] | _Sequence[RawCSS]
_TransformBox: TypeAlias = Literal[
    "border-box", "content-box", "fill-box", "stroke-box", "view-box"
]
_TransformOrigin: TypeAlias = (
    Length
    | Literal["bottom", "center", "left", "right", "top"]
    | Literal[0]
    | Percentage
    | tuple[
        Length
        | Literal["bottom", "center", "left", "right", "top"]
        | Literal[0]
        | Percentage,
        ...,
    ]
)
_TransformStyle: TypeAlias = Literal["flat", "preserve-3d"]
_Transition: TypeAlias = _Comma[
    RawCSS | Time | str | tuple[RawCSS | Time | str, ...]
]
_TransitionBehavior: TypeAlias = _Comma[Literal["allow-discrete", "normal"]]
_TransitionDelay: TypeAlias = _Comma[Time]
_TransitionDuration: TypeAlias = _Comma[Time]
_TransitionProperty: TypeAlias = Literal["none"] | _Comma[str]
_TransitionTimingFunction: TypeAlias = _AnimationTimingFunction
_Translate: TypeAlias = (
    Length
    | Literal["none"]
    | Literal[0]
    | Percentage
    | tuple[Length | Literal[0] | Percentage, ...]
)
_TriggerScope: TypeAlias = Literal["all", "none"] | _Comma[str]
_Types: TypeAlias = Literal["none"] | _Sequence[str]
_UnicodeBidi: TypeAlias = Literal[
    "bidi-override",
    "embed",
    "isolate",
    "isolate-override",
    "normal",
    "plaintext",
]
_UnicodeRange: TypeAlias = _Comma[str]
_UserSelect: TypeAlias = Literal["all", "auto", "none", "text"]
_VectorEffect: TypeAlias = Literal[
    "fixed-position",
    "non-rotation",
    "non-scaling-size",
    "non-scaling-stroke",
    "none",
]
_VerticalAlign: TypeAlias = (
    Length
    | Literal[
        "baseline",
        "bottom",
        "middle",
        "sub",
        "super",
        "text-bottom",
        "text-top",
        "top",
    ]
    | Literal[0]
    | Percentage
)
_ViewTimeline: TypeAlias = _Comma[
    _Comma[str] | tuple[Length | Literal[0] | Percentage | str, ...]
]
_ViewTimelineAxis: TypeAlias = _Comma[Literal["block", "inline", "x", "y"]]
_ViewTimelineInset: TypeAlias = _Comma[
    _Pair[Length | Literal["auto"] | Literal[0] | Percentage]
]
_ViewTimelineName: TypeAlias = _Comma[str]
_ViewTransitionClass: TypeAlias = Literal["none"] | _Sequence[str]
_ViewTransitionName: TypeAlias = str
_ViewTransitionScope: TypeAlias = Literal["all", "none"]
_Visibility: TypeAlias = Literal["collapse", "hidden", "visible"]
_WhiteSpace: TypeAlias = Literal[
    "break-spaces",
    "break-spaces nowrap",
    "break-spaces wrap",
    "collapse",
    "collapse nowrap",
    "collapse wrap",
    "normal",
    "nowrap",
    "nowrap break-spaces",
    "nowrap collapse",
    "nowrap preserve",
    "nowrap preserve-breaks",
    "nowrap preserve-spaces",
    "pre",
    "pre-line",
    "pre-wrap",
    "preserve",
    "preserve nowrap",
    "preserve wrap",
    "preserve-breaks",
    "preserve-breaks nowrap",
    "preserve-breaks wrap",
    "preserve-spaces",
    "preserve-spaces nowrap",
    "preserve-spaces wrap",
    "wrap",
    "wrap break-spaces",
    "wrap collapse",
    "wrap preserve",
    "wrap preserve-breaks",
    "wrap preserve-spaces",
]
_WhiteSpaceCollapse: TypeAlias = Literal[
    "break-spaces",
    "collapse",
    "preserve",
    "preserve-breaks",
    "preserve-spaces",
]
_Widows: TypeAlias = int
_Width: TypeAlias = _BlockSize
_WillChange: TypeAlias = Literal["auto"] | _Comma[str]
_WindowDrag: TypeAlias = Literal["move", "none"]
_WordBreak: TypeAlias = Literal[
    "auto-phrase", "break-all", "break-word", "keep-all", "normal"
]
_WordSpacing: TypeAlias = Length | Literal["normal"] | Literal[0]
_WordWrap: TypeAlias = Literal["break-word", "normal"]
_WritingMode: TypeAlias = Literal[
    "horizontal-tb", "sideways-lr", "sideways-rl", "vertical-lr", "vertical-rl"
]
_X: TypeAlias = Length | Literal[0] | Percentage
_Y: TypeAlias = Length | Literal[0] | Percentage
_ZIndex: TypeAlias = Literal["auto"] | int
_Zoom: TypeAlias = (
    Literal["normal", "reset"]
    | Percentage
    | float
    | tuple[Percentage | float, ...]
)
_MozAppearance: TypeAlias = Literal[
    "-moz-mac-unified-toolbar",
    "-moz-win-borderless-glass",
    "-moz-win-browsertabbar-toolbox",
    "-moz-win-communications-toolbox",
    "-moz-win-communicationstext",
    "-moz-win-exclude-glass",
    "-moz-win-glass",
    "-moz-win-media-toolbox",
    "-moz-win-mediatext",
    "-moz-window-button-box",
    "-moz-window-button-box-maximized",
    "-moz-window-button-close",
    "-moz-window-button-maximize",
    "-moz-window-button-minimize",
    "-moz-window-button-restore",
    "-moz-window-frame-bottom",
    "-moz-window-frame-left",
    "-moz-window-frame-right",
    "-moz-window-titlebar",
    "-moz-window-titlebar-maximized",
    "button",
    "button-arrow-down",
    "button-arrow-next",
    "button-arrow-previous",
    "button-arrow-up",
    "button-bevel",
    "button-focus",
    "caret",
    "checkbox",
    "checkbox-container",
    "checkbox-label",
    "checkmenuitem",
    "dualbutton",
    "groupbox",
    "listbox",
    "listitem",
    "menuarrow",
    "menubar",
    "menucheckbox",
    "menuimage",
    "menuitem",
    "menuitemtext",
    "menulist",
    "menulist-button",
    "menulist-text",
    "menulist-textfield",
    "menupopup",
    "menuradio",
    "menuseparator",
    "meterbar",
    "meterchunk",
    "none",
    "progressbar",
    "progressbar-vertical",
    "progresschunk",
    "progresschunk-vertical",
    "radio",
    "radio-container",
    "radio-label",
    "radiomenuitem",
    "range",
    "range-thumb",
    "resizer",
    "resizerpanel",
    "scale-horizontal",
    "scale-vertical",
    "scalethumb-horizontal",
    "scalethumb-vertical",
    "scalethumbend",
    "scalethumbstart",
    "scalethumbtick",
    "scrollbarbutton-down",
    "scrollbarbutton-left",
    "scrollbarbutton-right",
    "scrollbarbutton-up",
    "scrollbarthumb-horizontal",
    "scrollbarthumb-vertical",
    "scrollbartrack-horizontal",
    "scrollbartrack-vertical",
    "searchfield",
    "separator",
    "sheet",
    "spinner",
    "spinner-downbutton",
    "spinner-textfield",
    "spinner-upbutton",
    "splitter",
    "statusbar",
    "statusbarpanel",
    "tab",
    "tab-scroll-arrow-back",
    "tab-scroll-arrow-forward",
    "tabpanel",
    "tabpanels",
    "textfield",
    "textfield-multiline",
    "toolbar",
    "toolbarbutton",
    "toolbarbutton-dropdown",
    "toolbargripper",
    "toolbox",
    "tooltip",
    "treeheader",
    "treeheadercell",
    "treeheadersortarrow",
    "treeitem",
    "treeline",
    "treetwisty",
    "treetwistyopen",
    "treeview",
]
_MozBinding: TypeAlias = str
_MozBorderBottomColors: TypeAlias = Literal["none"] | _Sequence[str]
_MozBorderLeftColors: TypeAlias = Literal["none"] | _Sequence[str]
_MozBorderRightColors: TypeAlias = Literal["none"] | _Sequence[str]
_MozBorderTopColors: TypeAlias = Literal["none"] | _Sequence[str]
_MozContextProperties: TypeAlias = (
    Literal["none"]
    | _Comma[Literal["fill", "fill-opacity", "stroke", "stroke-opacity"]]
)
_MozFloatEdge: TypeAlias = Literal[
    "border-box", "content-box", "margin-box", "padding-box"
]
_MozForceBrokenImageIcon: TypeAlias = Literal["1"] | Literal[0]
_MozOrient: TypeAlias = Literal["block", "horizontal", "inline", "vertical"]
_MozOutlineRadius: TypeAlias = _BorderRadius
_MozOutlineRadiusBottomleft: TypeAlias = Length | Literal[0] | Percentage
_MozOutlineRadiusBottomright: TypeAlias = Length | Literal[0] | Percentage
_MozOutlineRadiusTopleft: TypeAlias = Length | Literal[0] | Percentage
_MozOutlineRadiusTopright: TypeAlias = Length | Literal[0] | Percentage
_MozStackSizing: TypeAlias = Literal["ignore", "stretch-to-fit"]
_MozTextBlink: TypeAlias = Literal["blink", "none"]
_MozUserFocus: TypeAlias = Literal[
    "ignore",
    "none",
    "normal",
    "select-after",
    "select-all",
    "select-before",
    "select-menu",
    "select-same",
]
_MozUserInput: TypeAlias = Literal["auto", "disabled", "enabled", "none"]
_MozUserModify: TypeAlias = Literal["read-only", "read-write", "write-only"]
_MozWindowDragging: TypeAlias = Literal["drag", "no-drag"]
_MozWindowShadow: TypeAlias = Literal[
    "default", "menu", "none", "sheet", "tooltip"
]
_MsAccelerator: TypeAlias = Literal["false", "true"]
_MsBlockProgression: TypeAlias = Literal["bt", "lr", "rl", "tb"]
_MsContentZoomChaining: TypeAlias = Literal["chained", "none"]
_MsContentZoomLimit: TypeAlias = tuple[Percentage, ...]
_MsContentZoomLimitMax: TypeAlias = Percentage
_MsContentZoomLimitMin: TypeAlias = Percentage
_MsContentZoomSnap: TypeAlias = (
    Literal["mandatory", "none", "proximity"]
    | RawCSS
    | tuple[Literal["mandatory", "none", "proximity"] | RawCSS, ...]
)
_MsContentZoomSnapPoints: TypeAlias = RawCSS
_MsContentZoomSnapType: TypeAlias = Literal["mandatory", "none", "proximity"]
_MsContentZooming: TypeAlias = Literal["none", "zoom"]
_MsFilter: TypeAlias = str
_MsFlowFrom: TypeAlias = _Comma[str]
_MsFlowInto: TypeAlias = _Comma[str]
_MsGridColumns: TypeAlias = (
    Literal["none"]
    | RawCSS
    | _Sequence[
        Fractions
        | Length
        | Literal["auto", "max-content", "min-content"]
        | Literal[0]
        | Percentage
        | RawCSS
        | tuple[
            Fractions | Length | Literal[0] | Percentage | RawCSS | str, ...
        ]
    ]
    | tuple[Fractions | Length | Literal[0] | Percentage | RawCSS | str, ...]
    | tuple[Length | Literal[0] | Percentage | RawCSS | str, ...]
)
_MsGridRows: TypeAlias = _MsGridColumns
_MsHighContrastAdjust: TypeAlias = Literal["auto", "none"]
_MsHyphenateLimitChars: TypeAlias = Literal["auto"] | _Triple[int]
_MsHyphenateLimitLines: TypeAlias = Literal["no-limit"] | int
_MsHyphenateLimitZone: TypeAlias = Length | Literal[0] | Percentage
_MsImeAlign: TypeAlias = Literal["after", "auto"]
_MsOverflowStyle: TypeAlias = Literal[
    "-ms-autohiding-scrollbar", "auto", "none", "scrollbar"
]
_MsScrollChaining: TypeAlias = Literal["chained", "none"]
_MsScrollLimit: TypeAlias = tuple[Length | Literal["auto"] | Literal[0], ...]
_MsScrollLimitXMax: TypeAlias = Length | Literal["auto"] | Literal[0]
_MsScrollLimitXMin: TypeAlias = Length | Literal[0]
_MsScrollLimitYMax: TypeAlias = Length | Literal["auto"] | Literal[0]
_MsScrollLimitYMin: TypeAlias = Length | Literal[0]
_MsScrollRails: TypeAlias = Literal["none", "railed"]
_MsScrollSnapPointsX: TypeAlias = RawCSS
_MsScrollSnapPointsY: TypeAlias = RawCSS
_MsScrollSnapType: TypeAlias = Literal["mandatory", "none", "proximity"]
_MsScrollSnapX: TypeAlias = tuple[
    Literal["mandatory", "none", "proximity"] | RawCSS, ...
]
_MsScrollSnapY: TypeAlias = tuple[
    Literal["mandatory", "none", "proximity"] | RawCSS, ...
]
_MsScrollTranslation: TypeAlias = Literal["none", "vertical-to-horizontal"]
_MsScrollbar3dlightColor: TypeAlias = str
_MsScrollbarArrowColor: TypeAlias = str
_MsScrollbarBaseColor: TypeAlias = str
_MsScrollbarDarkshadowColor: TypeAlias = str
_MsScrollbarFaceColor: TypeAlias = str
_MsScrollbarHighlightColor: TypeAlias = str
_MsScrollbarShadowColor: TypeAlias = str
_MsScrollbarTrackColor: TypeAlias = str
_MsTextAutospace: TypeAlias = Literal[
    "ideograph-alpha",
    "ideograph-numeric",
    "ideograph-parenthesis",
    "ideograph-space",
    "none",
]
_MsTouchSelect: TypeAlias = Literal["grippers", "none"]
_MsUserSelect: TypeAlias = Literal["element", "none", "text"]
_MsWrapFlow: TypeAlias = Literal[
    "auto", "both", "clear", "end", "maximum", "start"
]
_MsWrapMargin: TypeAlias = Length | Literal[0]
_MsWrapThrough: TypeAlias = Literal["none", "wrap"]
_WebkitAppearance: TypeAlias = Literal[
    "-apple-pay-button",
    "button",
    "button-bevel",
    "caret",
    "checkbox",
    "default-button",
    "inner-spin-button",
    "listbox",
    "listitem",
    "media-controls-background",
    "media-controls-fullscreen-background",
    "media-current-time-display",
    "media-enter-fullscreen-button",
    "media-exit-fullscreen-button",
    "media-fullscreen-button",
    "media-mute-button",
    "media-overlay-play-button",
    "media-play-button",
    "media-seek-back-button",
    "media-seek-forward-button",
    "media-slider",
    "media-sliderthumb",
    "media-time-remaining-display",
    "media-toggle-closed-captions-button",
    "media-volume-slider",
    "media-volume-slider-container",
    "media-volume-sliderthumb",
    "menulist",
    "menulist-button",
    "menulist-text",
    "menulist-textfield",
    "meter",
    "none",
    "progress-bar",
    "progress-bar-value",
    "push-button",
    "radio",
    "searchfield",
    "searchfield-cancel-button",
    "searchfield-decoration",
    "searchfield-results-button",
    "searchfield-results-decoration",
    "slider-horizontal",
    "slider-vertical",
    "sliderthumb-horizontal",
    "sliderthumb-vertical",
    "square-button",
    "textarea",
    "textfield",
]
_WebkitBorderAfter: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_WebkitBorderAfterColor: TypeAlias = str
_WebkitBorderAfterStyle: TypeAlias = _BorderBlockEndStyle
_WebkitBorderAfterWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_WebkitBorderBefore: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_WebkitBorderBeforeColor: TypeAlias = str
_WebkitBorderBeforeStyle: TypeAlias = _BorderBlockEndStyle
_WebkitBorderBeforeWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_WebkitBorderEnd: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_WebkitBorderEndColor: TypeAlias = str
_WebkitBorderEndStyle: TypeAlias = _BorderBlockEndStyle
_WebkitBorderEndWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_WebkitBorderStart: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_WebkitBorderStartColor: TypeAlias = str
_WebkitBorderStartStyle: TypeAlias = _BorderBlockEndStyle
_WebkitBorderStartWidth: TypeAlias = (
    Length | Literal["medium", "thick", "thin"] | Literal[0]
)
_WebkitBoxReflect: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_WebkitLineClamp: TypeAlias = Literal["none"] | int
_WebkitMask: TypeAlias = _Mask
_WebkitMaskAttachment: TypeAlias = _Comma[Literal["fixed", "local", "scroll"]]
_WebkitMaskClip: TypeAlias = _Comma[
    Literal[
        "border",
        "border-box",
        "content",
        "content-box",
        "fill-box",
        "no-clip",
        "padding",
        "padding-box",
        "stroke-box",
        "text",
        "view-box",
    ]
]
_WebkitMaskComposite: TypeAlias = _Comma[
    Literal[
        "clear",
        "copy",
        "destination-atop",
        "destination-in",
        "destination-out",
        "destination-over",
        "source-atop",
        "source-in",
        "source-out",
        "source-over",
        "xor",
    ]
]
_WebkitMaskImage: TypeAlias = _Comma[str]
_WebkitMaskOrigin: TypeAlias = _Comma[
    Literal[
        "border",
        "border-box",
        "content",
        "content-box",
        "fill-box",
        "padding",
        "padding-box",
        "stroke-box",
        "view-box",
    ]
]
_WebkitMaskPosition: TypeAlias = _MaskPosition
_WebkitMaskPositionX: TypeAlias = _Comma[
    Length | Literal["center", "left", "right"] | Literal[0] | Percentage
]
_WebkitMaskPositionY: TypeAlias = _Comma[
    Length | Literal["bottom", "center", "top"] | Literal[0] | Percentage
]
_WebkitMaskRepeat: TypeAlias = _BackgroundRepeat
_WebkitMaskRepeatX: TypeAlias = Literal[
    "no-repeat", "repeat", "round", "space"
]
_WebkitMaskRepeatY: TypeAlias = Literal[
    "no-repeat", "repeat", "round", "space"
]
_WebkitMaskSize: TypeAlias = _BackgroundSize
_WebkitOverflowScrolling: TypeAlias = Literal["auto", "touch"]
_WebkitTapHighlightColor: TypeAlias = str
_WebkitTextFillColor: TypeAlias = str
_WebkitTextStroke: TypeAlias = (
    Length | Literal[0] | str | tuple[Length | Literal[0] | str, ...]
)
_WebkitTextStrokeColor: TypeAlias = str
_WebkitTextStrokeWidth: TypeAlias = Length | Literal[0]
_WebkitTouchCallout: TypeAlias = Literal["default", "none"]
_WebkitUserModify: TypeAlias = Literal[
    "read-only", "read-write", "read-write-plaintext-only"
]
_WebkitUserSelect: TypeAlias = Literal["all", "auto", "none", "text"]


class CSSProperties(TypedDict, total=False):
    accent_color: PropertyValue[_AccentColor]
    additive_symbols: PropertyValue[_AdditiveSymbols]
    align_content: PropertyValue[_AlignContent]
    align_items: PropertyValue[_AlignItems]
    align_self: PropertyValue[_AlignSelf]
    align_tracks: PropertyValue[_AlignTracks]
    alignment_baseline: PropertyValue[_AlignmentBaseline]
    all: PropertyValue[_All]
    anchor_name: PropertyValue[_AnchorName]
    anchor_scope: PropertyValue[_AnchorScope]
    animation: PropertyValue[_Animation]
    animation_composition: PropertyValue[_AnimationComposition]
    animation_delay: PropertyValue[_AnimationDelay]
    animation_direction: PropertyValue[_AnimationDirection]
    animation_duration: PropertyValue[_AnimationDuration]
    animation_fill_mode: PropertyValue[_AnimationFillMode]
    animation_iteration_count: PropertyValue[_AnimationIterationCount]
    animation_name: PropertyValue[_AnimationName]
    animation_play_state: PropertyValue[_AnimationPlayState]
    animation_range: PropertyValue[_AnimationRange]
    animation_range_end: PropertyValue[_AnimationRangeEnd]
    animation_range_start: PropertyValue[_AnimationRangeStart]
    animation_timeline: PropertyValue[_AnimationTimeline]
    animation_timing_function: PropertyValue[_AnimationTimingFunction]
    animation_trigger: PropertyValue[_AnimationTrigger]
    appearance: PropertyValue[_Appearance]
    ascent_override: PropertyValue[_AscentOverride]
    aspect_ratio: PropertyValue[_AspectRatio]
    backdrop_filter: PropertyValue[_BackdropFilter]
    backface_visibility: PropertyValue[_BackfaceVisibility]
    background: PropertyValue[_Background]
    background_attachment: PropertyValue[_BackgroundAttachment]
    background_blend_mode: PropertyValue[_BackgroundBlendMode]
    background_clip: PropertyValue[_BackgroundClip]
    background_color: PropertyValue[_BackgroundColor]
    background_image: PropertyValue[_BackgroundImage]
    background_origin: PropertyValue[_BackgroundOrigin]
    background_position: PropertyValue[_BackgroundPosition]
    background_position_x: PropertyValue[_BackgroundPositionX]
    background_position_y: PropertyValue[_BackgroundPositionY]
    background_repeat: PropertyValue[_BackgroundRepeat]
    background_size: PropertyValue[_BackgroundSize]
    base_palette: PropertyValue[_BasePalette]
    baseline_shift: PropertyValue[_BaselineShift]
    baseline_source: PropertyValue[_BaselineSource]
    bleed: PropertyValue[_Bleed]
    block_size: PropertyValue[_BlockSize]
    border: PropertyValue[_Border]
    border_block: PropertyValue[_BorderBlock]
    border_block_color: PropertyValue[_BorderBlockColor]
    border_block_end: PropertyValue[_BorderBlockEnd]
    border_block_end_color: PropertyValue[_BorderBlockEndColor]
    border_block_end_style: PropertyValue[_BorderBlockEndStyle]
    border_block_end_width: PropertyValue[_BorderBlockEndWidth]
    border_block_start: PropertyValue[_BorderBlockStart]
    border_block_start_color: PropertyValue[_BorderBlockStartColor]
    border_block_start_style: PropertyValue[_BorderBlockStartStyle]
    border_block_start_width: PropertyValue[_BorderBlockStartWidth]
    border_block_style: PropertyValue[_BorderBlockStyle]
    border_block_width: PropertyValue[_BorderBlockWidth]
    border_bottom: PropertyValue[_BorderBottom]
    border_bottom_color: PropertyValue[_BorderBottomColor]
    border_bottom_left_radius: PropertyValue[_BorderBottomLeftRadius]
    border_bottom_right_radius: PropertyValue[_BorderBottomRightRadius]
    border_bottom_style: PropertyValue[_BorderBottomStyle]
    border_bottom_width: PropertyValue[_BorderBottomWidth]
    border_collapse: PropertyValue[_BorderCollapse]
    border_color: PropertyValue[_BorderColor]
    border_end_end_radius: PropertyValue[_BorderEndEndRadius]
    border_end_start_radius: PropertyValue[_BorderEndStartRadius]
    border_image: PropertyValue[_BorderImage]
    border_image_outset: PropertyValue[_BorderImageOutset]
    border_image_repeat: PropertyValue[_BorderImageRepeat]
    border_image_slice: PropertyValue[_BorderImageSlice]
    border_image_source: PropertyValue[_BorderImageSource]
    border_image_width: PropertyValue[_BorderImageWidth]
    border_inline: PropertyValue[_BorderInline]
    border_inline_color: PropertyValue[_BorderInlineColor]
    border_inline_end: PropertyValue[_BorderInlineEnd]
    border_inline_end_color: PropertyValue[_BorderInlineEndColor]
    border_inline_end_style: PropertyValue[_BorderInlineEndStyle]
    border_inline_end_width: PropertyValue[_BorderInlineEndWidth]
    border_inline_start: PropertyValue[_BorderInlineStart]
    border_inline_start_color: PropertyValue[_BorderInlineStartColor]
    border_inline_start_style: PropertyValue[_BorderInlineStartStyle]
    border_inline_start_width: PropertyValue[_BorderInlineStartWidth]
    border_inline_style: PropertyValue[_BorderInlineStyle]
    border_inline_width: PropertyValue[_BorderInlineWidth]
    border_left: PropertyValue[_BorderLeft]
    border_left_color: PropertyValue[_BorderLeftColor]
    border_left_style: PropertyValue[_BorderLeftStyle]
    border_left_width: PropertyValue[_BorderLeftWidth]
    border_radius: PropertyValue[_BorderRadius]
    border_right: PropertyValue[_BorderRight]
    border_right_color: PropertyValue[_BorderRightColor]
    border_right_style: PropertyValue[_BorderRightStyle]
    border_right_width: PropertyValue[_BorderRightWidth]
    border_shape: PropertyValue[_BorderShape]
    border_spacing: PropertyValue[_BorderSpacing]
    border_start_end_radius: PropertyValue[_BorderStartEndRadius]
    border_start_start_radius: PropertyValue[_BorderStartStartRadius]
    border_style: PropertyValue[_BorderStyle]
    border_top: PropertyValue[_BorderTop]
    border_top_color: PropertyValue[_BorderTopColor]
    border_top_left_radius: PropertyValue[_BorderTopLeftRadius]
    border_top_right_radius: PropertyValue[_BorderTopRightRadius]
    border_top_style: PropertyValue[_BorderTopStyle]
    border_top_width: PropertyValue[_BorderTopWidth]
    border_width: PropertyValue[_BorderWidth]
    bottom: PropertyValue[_Bottom]
    box_align: PropertyValue[_BoxAlign]
    box_decoration_break: PropertyValue[_BoxDecorationBreak]
    box_direction: PropertyValue[_BoxDirection]
    box_flex: PropertyValue[_BoxFlex]
    box_flex_group: PropertyValue[_BoxFlexGroup]
    box_lines: PropertyValue[_BoxLines]
    box_ordinal_group: PropertyValue[_BoxOrdinalGroup]
    box_orient: PropertyValue[_BoxOrient]
    box_pack: PropertyValue[_BoxPack]
    box_shadow: PropertyValue[_BoxShadow]
    box_sizing: PropertyValue[_BoxSizing]
    break_after: PropertyValue[_BreakAfter]
    break_before: PropertyValue[_BreakBefore]
    break_inside: PropertyValue[_BreakInside]
    caption_side: PropertyValue[_CaptionSide]
    caret: PropertyValue[_Caret]
    caret_animation: PropertyValue[_CaretAnimation]
    caret_color: PropertyValue[_CaretColor]
    caret_shape: PropertyValue[_CaretShape]
    clear: PropertyValue[_Clear]
    clip: PropertyValue[_Clip]
    clip_path: PropertyValue[_ClipPath]
    clip_rule: PropertyValue[_ClipRule]
    color: PropertyValue[_Color]
    color_interpolation_filters: PropertyValue[_ColorInterpolationFilters]
    color_scheme: PropertyValue[_ColorScheme]
    column_count: PropertyValue[_ColumnCount]
    column_fill: PropertyValue[_ColumnFill]
    column_gap: PropertyValue[_ColumnGap]
    column_height: PropertyValue[_ColumnHeight]
    column_rule: PropertyValue[_ColumnRule]
    column_rule_color: PropertyValue[_ColumnRuleColor]
    column_rule_style: PropertyValue[_ColumnRuleStyle]
    column_rule_width: PropertyValue[_ColumnRuleWidth]
    column_span: PropertyValue[_ColumnSpan]
    column_width: PropertyValue[_ColumnWidth]
    column_wrap: PropertyValue[_ColumnWrap]
    columns: PropertyValue[_Columns]
    contain: PropertyValue[_Contain]
    contain_intrinsic_block_size: PropertyValue[_ContainIntrinsicBlockSize]
    contain_intrinsic_height: PropertyValue[_ContainIntrinsicHeight]
    contain_intrinsic_inline_size: PropertyValue[_ContainIntrinsicInlineSize]
    contain_intrinsic_size: PropertyValue[_ContainIntrinsicSize]
    contain_intrinsic_width: PropertyValue[_ContainIntrinsicWidth]
    container: PropertyValue[_Container]
    container_name: PropertyValue[_ContainerName]
    container_type: PropertyValue[_ContainerType]
    content: PropertyValue[_Content]
    content_visibility: PropertyValue[_ContentVisibility]
    corner_block_end_shape: PropertyValue[_CornerBlockEndShape]
    corner_block_start_shape: PropertyValue[_CornerBlockStartShape]
    corner_bottom_left_shape: PropertyValue[_CornerBottomLeftShape]
    corner_bottom_right_shape: PropertyValue[_CornerBottomRightShape]
    corner_bottom_shape: PropertyValue[_CornerBottomShape]
    corner_end_end_shape: PropertyValue[_CornerEndEndShape]
    corner_end_start_shape: PropertyValue[_CornerEndStartShape]
    corner_inline_end_shape: PropertyValue[_CornerInlineEndShape]
    corner_inline_start_shape: PropertyValue[_CornerInlineStartShape]
    corner_left_shape: PropertyValue[_CornerLeftShape]
    corner_right_shape: PropertyValue[_CornerRightShape]
    corner_shape: PropertyValue[_CornerShape]
    corner_start_end_shape: PropertyValue[_CornerStartEndShape]
    corner_start_start_shape: PropertyValue[_CornerStartStartShape]
    corner_top_left_shape: PropertyValue[_CornerTopLeftShape]
    corner_top_right_shape: PropertyValue[_CornerTopRightShape]
    corner_top_shape: PropertyValue[_CornerTopShape]
    counter_increment: PropertyValue[_CounterIncrement]
    counter_reset: PropertyValue[_CounterReset]
    counter_set: PropertyValue[_CounterSet]
    cursor: PropertyValue[_Cursor]
    cx: PropertyValue[_Cx]
    cy: PropertyValue[_Cy]
    d: PropertyValue[_D]
    descent_override: PropertyValue[_DescentOverride]
    direction: PropertyValue[_Direction]
    display: PropertyValue[_Display]
    dominant_baseline: PropertyValue[_DominantBaseline]
    dynamic_range_limit: PropertyValue[_DynamicRangeLimit]
    empty_cells: PropertyValue[_EmptyCells]
    fallback: PropertyValue[_Fallback]
    field_sizing: PropertyValue[_FieldSizing]
    fill: PropertyValue[_Fill]
    fill_opacity: PropertyValue[_FillOpacity]
    fill_rule: PropertyValue[_FillRule]
    filter: PropertyValue[_Filter]
    flex: PropertyValue[_Flex]
    flex_basis: PropertyValue[_FlexBasis]
    flex_direction: PropertyValue[_FlexDirection]
    flex_flow: PropertyValue[_FlexFlow]
    flex_grow: PropertyValue[_FlexGrow]
    flex_line_count: PropertyValue[_FlexLineCount]
    flex_shrink: PropertyValue[_FlexShrink]
    flex_wrap: PropertyValue[_FlexWrap]
    float: PropertyValue[_Float]
    flood_color: PropertyValue[_FloodColor]
    flood_opacity: PropertyValue[_FloodOpacity]
    font: PropertyValue[_Font]
    font_display: PropertyValue[_FontDisplay]
    font_family: PropertyValue[_FontFamily]
    font_feature_settings: PropertyValue[_FontFeatureSettings]
    font_kerning: PropertyValue[_FontKerning]
    font_language_override: PropertyValue[_FontLanguageOverride]
    font_optical_sizing: PropertyValue[_FontOpticalSizing]
    font_palette: PropertyValue[_FontPalette]
    font_size: PropertyValue[_FontSize]
    font_size_adjust: PropertyValue[_FontSizeAdjust]
    font_smooth: PropertyValue[_FontSmooth]
    font_stretch: PropertyValue[_FontStretch]
    font_style: PropertyValue[_FontStyle]
    font_synthesis: PropertyValue[_FontSynthesis]
    font_synthesis_position: PropertyValue[_FontSynthesisPosition]
    font_synthesis_small_caps: PropertyValue[_FontSynthesisSmallCaps]
    font_synthesis_style: PropertyValue[_FontSynthesisStyle]
    font_synthesis_weight: PropertyValue[_FontSynthesisWeight]
    font_variant: PropertyValue[_FontVariant]
    font_variant_alternates: PropertyValue[_FontVariantAlternates]
    font_variant_caps: PropertyValue[_FontVariantCaps]
    font_variant_east_asian: PropertyValue[_FontVariantEastAsian]
    font_variant_emoji: PropertyValue[_FontVariantEmoji]
    font_variant_ligatures: PropertyValue[_FontVariantLigatures]
    font_variant_numeric: PropertyValue[_FontVariantNumeric]
    font_variant_position: PropertyValue[_FontVariantPosition]
    font_variation_settings: PropertyValue[_FontVariationSettings]
    font_weight: PropertyValue[_FontWeight]
    font_width: PropertyValue[_FontWidth]
    forced_color_adjust: PropertyValue[_ForcedColorAdjust]
    frame_sizing: PropertyValue[_FrameSizing]
    gap: PropertyValue[_Gap]
    grid: PropertyValue[_Grid]
    grid_area: PropertyValue[_GridArea]
    grid_auto_columns: PropertyValue[_GridAutoColumns]
    grid_auto_flow: PropertyValue[_GridAutoFlow]
    grid_auto_rows: PropertyValue[_GridAutoRows]
    grid_column: PropertyValue[_GridColumn]
    grid_column_end: PropertyValue[_GridColumnEnd]
    grid_column_gap: PropertyValue[_GridColumnGap]
    grid_column_start: PropertyValue[_GridColumnStart]
    grid_gap: PropertyValue[_GridGap]
    grid_row: PropertyValue[_GridRow]
    grid_row_end: PropertyValue[_GridRowEnd]
    grid_row_gap: PropertyValue[_GridRowGap]
    grid_row_start: PropertyValue[_GridRowStart]
    grid_template: PropertyValue[_GridTemplate]
    grid_template_areas: PropertyValue[_GridTemplateAreas]
    grid_template_columns: PropertyValue[_GridTemplateColumns]
    grid_template_rows: PropertyValue[_GridTemplateRows]
    hanging_punctuation: PropertyValue[_HangingPunctuation]
    height: PropertyValue[_Height]
    hyphenate_character: PropertyValue[_HyphenateCharacter]
    hyphenate_limit_chars: PropertyValue[_HyphenateLimitChars]
    hyphens: PropertyValue[_Hyphens]
    image_orientation: PropertyValue[_ImageOrientation]
    image_rendering: PropertyValue[_ImageRendering]
    image_resolution: PropertyValue[_ImageResolution]
    ime_mode: PropertyValue[_ImeMode]
    inherits: PropertyValue[_Inherits]
    initial_letter: PropertyValue[_InitialLetter]
    initial_letter_align: PropertyValue[_InitialLetterAlign]
    initial_value: PropertyValue[_InitialValue]
    inline_size: PropertyValue[_InlineSize]
    inset: PropertyValue[_Inset]
    inset_block: PropertyValue[_InsetBlock]
    inset_block_end: PropertyValue[_InsetBlockEnd]
    inset_block_start: PropertyValue[_InsetBlockStart]
    inset_inline: PropertyValue[_InsetInline]
    inset_inline_end: PropertyValue[_InsetInlineEnd]
    inset_inline_start: PropertyValue[_InsetInlineStart]
    interactivity: PropertyValue[_Interactivity]
    interest_delay: PropertyValue[_InterestDelay]
    interest_delay_end: PropertyValue[_InterestDelayEnd]
    interest_delay_start: PropertyValue[_InterestDelayStart]
    interpolate_size: PropertyValue[_InterpolateSize]
    isolation: PropertyValue[_Isolation]
    justify_content: PropertyValue[_JustifyContent]
    justify_items: PropertyValue[_JustifyItems]
    justify_self: PropertyValue[_JustifySelf]
    justify_tracks: PropertyValue[_JustifyTracks]
    left: PropertyValue[_Left]
    letter_spacing: PropertyValue[_LetterSpacing]
    lighting_color: PropertyValue[_LightingColor]
    line_break: PropertyValue[_LineBreak]
    line_clamp: PropertyValue[_LineClamp]
    line_gap_override: PropertyValue[_LineGapOverride]
    line_height: PropertyValue[_LineHeight]
    line_height_step: PropertyValue[_LineHeightStep]
    link_parameters: PropertyValue[_LinkParameters]
    list_style: PropertyValue[_ListStyle]
    list_style_image: PropertyValue[_ListStyleImage]
    list_style_position: PropertyValue[_ListStylePosition]
    list_style_type: PropertyValue[_ListStyleType]
    margin: PropertyValue[_Margin]
    margin_block: PropertyValue[_MarginBlock]
    margin_block_end: PropertyValue[_MarginBlockEnd]
    margin_block_start: PropertyValue[_MarginBlockStart]
    margin_bottom: PropertyValue[_MarginBottom]
    margin_inline: PropertyValue[_MarginInline]
    margin_inline_end: PropertyValue[_MarginInlineEnd]
    margin_inline_start: PropertyValue[_MarginInlineStart]
    margin_left: PropertyValue[_MarginLeft]
    margin_right: PropertyValue[_MarginRight]
    margin_top: PropertyValue[_MarginTop]
    margin_trim: PropertyValue[_MarginTrim]
    marker: PropertyValue[_Marker]
    marker_end: PropertyValue[_MarkerEnd]
    marker_mid: PropertyValue[_MarkerMid]
    marker_start: PropertyValue[_MarkerStart]
    marks: PropertyValue[_Marks]
    mask: PropertyValue[_Mask]
    mask_border: PropertyValue[_MaskBorder]
    mask_border_mode: PropertyValue[_MaskBorderMode]
    mask_border_outset: PropertyValue[_MaskBorderOutset]
    mask_border_repeat: PropertyValue[_MaskBorderRepeat]
    mask_border_slice: PropertyValue[_MaskBorderSlice]
    mask_border_source: PropertyValue[_MaskBorderSource]
    mask_border_width: PropertyValue[_MaskBorderWidth]
    mask_clip: PropertyValue[_MaskClip]
    mask_composite: PropertyValue[_MaskComposite]
    mask_image: PropertyValue[_MaskImage]
    mask_mode: PropertyValue[_MaskMode]
    mask_origin: PropertyValue[_MaskOrigin]
    mask_position: PropertyValue[_MaskPosition]
    mask_repeat: PropertyValue[_MaskRepeat]
    mask_size: PropertyValue[_MaskSize]
    mask_type: PropertyValue[_MaskType]
    masonry_auto_flow: PropertyValue[_MasonryAutoFlow]
    math_depth: PropertyValue[_MathDepth]
    math_shift: PropertyValue[_MathShift]
    math_style: PropertyValue[_MathStyle]
    max_block_size: PropertyValue[_MaxBlockSize]
    max_height: PropertyValue[_MaxHeight]
    max_inline_size: PropertyValue[_MaxInlineSize]
    max_lines: PropertyValue[_MaxLines]
    max_width: PropertyValue[_MaxWidth]
    min_block_size: PropertyValue[_MinBlockSize]
    min_height: PropertyValue[_MinHeight]
    min_inline_size: PropertyValue[_MinInlineSize]
    min_width: PropertyValue[_MinWidth]
    mix_blend_mode: PropertyValue[_MixBlendMode]
    navigation: PropertyValue[_Navigation]
    negative: PropertyValue[_Negative]
    object_fit: PropertyValue[_ObjectFit]
    object_position: PropertyValue[_ObjectPosition]
    object_view_box: PropertyValue[_ObjectViewBox]
    offset: PropertyValue[_Offset]
    offset_anchor: PropertyValue[_OffsetAnchor]
    offset_distance: PropertyValue[_OffsetDistance]
    offset_path: PropertyValue[_OffsetPath]
    offset_position: PropertyValue[_OffsetPosition]
    offset_rotate: PropertyValue[_OffsetRotate]
    opacity: PropertyValue[_Opacity]
    order: PropertyValue[_Order]
    orphans: PropertyValue[_Orphans]
    outline: PropertyValue[_Outline]
    outline_color: PropertyValue[_OutlineColor]
    outline_offset: PropertyValue[_OutlineOffset]
    outline_style: PropertyValue[_OutlineStyle]
    outline_width: PropertyValue[_OutlineWidth]
    overflow: PropertyValue[_Overflow]
    overflow_anchor: PropertyValue[_OverflowAnchor]
    overflow_block: PropertyValue[_OverflowBlock]
    overflow_clip_box: PropertyValue[_OverflowClipBox]
    overflow_clip_margin: PropertyValue[_OverflowClipMargin]
    overflow_inline: PropertyValue[_OverflowInline]
    overflow_wrap: PropertyValue[_OverflowWrap]
    overflow_x: PropertyValue[_OverflowX]
    overflow_y: PropertyValue[_OverflowY]
    overlay: PropertyValue[_Overlay]
    override_colors: PropertyValue[_OverrideColors]
    overscroll_behavior: PropertyValue[_OverscrollBehavior]
    overscroll_behavior_block: PropertyValue[_OverscrollBehaviorBlock]
    overscroll_behavior_inline: PropertyValue[_OverscrollBehaviorInline]
    overscroll_behavior_x: PropertyValue[_OverscrollBehaviorX]
    overscroll_behavior_y: PropertyValue[_OverscrollBehaviorY]
    pad: PropertyValue[_Pad]
    padding: PropertyValue[_Padding]
    padding_block: PropertyValue[_PaddingBlock]
    padding_block_end: PropertyValue[_PaddingBlockEnd]
    padding_block_start: PropertyValue[_PaddingBlockStart]
    padding_bottom: PropertyValue[_PaddingBottom]
    padding_inline: PropertyValue[_PaddingInline]
    padding_inline_end: PropertyValue[_PaddingInlineEnd]
    padding_inline_start: PropertyValue[_PaddingInlineStart]
    padding_left: PropertyValue[_PaddingLeft]
    padding_right: PropertyValue[_PaddingRight]
    padding_top: PropertyValue[_PaddingTop]
    page: PropertyValue[_Page]
    page_break_after: PropertyValue[_PageBreakAfter]
    page_break_before: PropertyValue[_PageBreakBefore]
    page_break_inside: PropertyValue[_PageBreakInside]
    page_margin_safety: PropertyValue[_PageMarginSafety]
    page_orientation: PropertyValue[_PageOrientation]
    paint_order: PropertyValue[_PaintOrder]
    path_length: PropertyValue[_PathLength]
    perspective: PropertyValue[_Perspective]
    perspective_origin: PropertyValue[_PerspectiveOrigin]
    place_content: PropertyValue[_PlaceContent]
    place_items: PropertyValue[_PlaceItems]
    place_self: PropertyValue[_PlaceSelf]
    pointer_events: PropertyValue[_PointerEvents]
    position: PropertyValue[_Position]
    position_anchor: PropertyValue[_PositionAnchor]
    position_area: PropertyValue[_PositionArea]
    position_try: PropertyValue[_PositionTry]
    position_try_fallbacks: PropertyValue[_PositionTryFallbacks]
    position_try_order: PropertyValue[_PositionTryOrder]
    position_visibility: PropertyValue[_PositionVisibility]
    prefix: PropertyValue[_Prefix]
    print_color_adjust: PropertyValue[_PrintColorAdjust]
    quotes: PropertyValue[_Quotes]
    r: PropertyValue[_R]
    range: PropertyValue[_Range]
    reading_flow: PropertyValue[_ReadingFlow]
    reading_order: PropertyValue[_ReadingOrder]
    resize: PropertyValue[_Resize]
    right: PropertyValue[_Right]
    rotate: PropertyValue[_Rotate]
    row_gap: PropertyValue[_RowGap]
    ruby_align: PropertyValue[_RubyAlign]
    ruby_merge: PropertyValue[_RubyMerge]
    ruby_overhang: PropertyValue[_RubyOverhang]
    ruby_position: PropertyValue[_RubyPosition]
    rx: PropertyValue[_Rx]
    ry: PropertyValue[_Ry]
    scale: PropertyValue[_Scale]
    scroll_axis_lock: PropertyValue[_ScrollAxisLock]
    scroll_behavior: PropertyValue[_ScrollBehavior]
    scroll_initial_target: PropertyValue[_ScrollInitialTarget]
    scroll_margin: PropertyValue[_ScrollMargin]
    scroll_margin_block: PropertyValue[_ScrollMarginBlock]
    scroll_margin_block_end: PropertyValue[_ScrollMarginBlockEnd]
    scroll_margin_block_start: PropertyValue[_ScrollMarginBlockStart]
    scroll_margin_bottom: PropertyValue[_ScrollMarginBottom]
    scroll_margin_inline: PropertyValue[_ScrollMarginInline]
    scroll_margin_inline_end: PropertyValue[_ScrollMarginInlineEnd]
    scroll_margin_inline_start: PropertyValue[_ScrollMarginInlineStart]
    scroll_margin_left: PropertyValue[_ScrollMarginLeft]
    scroll_margin_right: PropertyValue[_ScrollMarginRight]
    scroll_margin_top: PropertyValue[_ScrollMarginTop]
    scroll_marker_group: PropertyValue[_ScrollMarkerGroup]
    scroll_padding: PropertyValue[_ScrollPadding]
    scroll_padding_block: PropertyValue[_ScrollPaddingBlock]
    scroll_padding_block_end: PropertyValue[_ScrollPaddingBlockEnd]
    scroll_padding_block_start: PropertyValue[_ScrollPaddingBlockStart]
    scroll_padding_bottom: PropertyValue[_ScrollPaddingBottom]
    scroll_padding_inline: PropertyValue[_ScrollPaddingInline]
    scroll_padding_inline_end: PropertyValue[_ScrollPaddingInlineEnd]
    scroll_padding_inline_start: PropertyValue[_ScrollPaddingInlineStart]
    scroll_padding_left: PropertyValue[_ScrollPaddingLeft]
    scroll_padding_right: PropertyValue[_ScrollPaddingRight]
    scroll_padding_top: PropertyValue[_ScrollPaddingTop]
    scroll_snap_align: PropertyValue[_ScrollSnapAlign]
    scroll_snap_coordinate: PropertyValue[_ScrollSnapCoordinate]
    scroll_snap_destination: PropertyValue[_ScrollSnapDestination]
    scroll_snap_points_x: PropertyValue[_ScrollSnapPointsX]
    scroll_snap_points_y: PropertyValue[_ScrollSnapPointsY]
    scroll_snap_stop: PropertyValue[_ScrollSnapStop]
    scroll_snap_type: PropertyValue[_ScrollSnapType]
    scroll_snap_type_x: PropertyValue[_ScrollSnapTypeX]
    scroll_snap_type_y: PropertyValue[_ScrollSnapTypeY]
    scroll_target_group: PropertyValue[_ScrollTargetGroup]
    scroll_timeline: PropertyValue[_ScrollTimeline]
    scroll_timeline_axis: PropertyValue[_ScrollTimelineAxis]
    scroll_timeline_name: PropertyValue[_ScrollTimelineName]
    scrollbar_color: PropertyValue[_ScrollbarColor]
    scrollbar_gutter: PropertyValue[_ScrollbarGutter]
    scrollbar_width: PropertyValue[_ScrollbarWidth]
    shape_image_threshold: PropertyValue[_ShapeImageThreshold]
    shape_margin: PropertyValue[_ShapeMargin]
    shape_outside: PropertyValue[_ShapeOutside]
    shape_rendering: PropertyValue[_ShapeRendering]
    size: PropertyValue[_Size]
    size_adjust: PropertyValue[_SizeAdjust]
    speak_as: PropertyValue[_SpeakAs]
    src: PropertyValue[_Src]
    stop_color: PropertyValue[_StopColor]
    stop_opacity: PropertyValue[_StopOpacity]
    stroke: PropertyValue[_Stroke]
    stroke_color: PropertyValue[_StrokeColor]
    stroke_dasharray: PropertyValue[_StrokeDasharray]
    stroke_dashoffset: PropertyValue[_StrokeDashoffset]
    stroke_linecap: PropertyValue[_StrokeLinecap]
    stroke_linejoin: PropertyValue[_StrokeLinejoin]
    stroke_miterlimit: PropertyValue[_StrokeMiterlimit]
    stroke_opacity: PropertyValue[_StrokeOpacity]
    stroke_width: PropertyValue[_StrokeWidth]
    suffix: PropertyValue[_Suffix]
    symbols: PropertyValue[_Symbols]
    syntax: PropertyValue[_Syntax]
    system: PropertyValue[_System]
    tab_size: PropertyValue[_TabSize]
    table_layout: PropertyValue[_TableLayout]
    text_align: PropertyValue[_TextAlign]
    text_align_last: PropertyValue[_TextAlignLast]
    text_anchor: PropertyValue[_TextAnchor]
    text_autospace: PropertyValue[_TextAutospace]
    text_box: PropertyValue[_TextBox]
    text_box_edge: PropertyValue[_TextBoxEdge]
    text_box_trim: PropertyValue[_TextBoxTrim]
    text_combine_upright: PropertyValue[_TextCombineUpright]
    text_decoration: PropertyValue[_TextDecoration]
    text_decoration_color: PropertyValue[_TextDecorationColor]
    text_decoration_inset: PropertyValue[_TextDecorationInset]
    text_decoration_line: PropertyValue[_TextDecorationLine]
    text_decoration_skip: PropertyValue[_TextDecorationSkip]
    text_decoration_skip_ink: PropertyValue[_TextDecorationSkipInk]
    text_decoration_style: PropertyValue[_TextDecorationStyle]
    text_decoration_thickness: PropertyValue[_TextDecorationThickness]
    text_emphasis: PropertyValue[_TextEmphasis]
    text_emphasis_color: PropertyValue[_TextEmphasisColor]
    text_emphasis_position: PropertyValue[_TextEmphasisPosition]
    text_emphasis_style: PropertyValue[_TextEmphasisStyle]
    text_fit: PropertyValue[_TextFit]
    text_indent: PropertyValue[_TextIndent]
    text_justify: PropertyValue[_TextJustify]
    text_orientation: PropertyValue[_TextOrientation]
    text_overflow: PropertyValue[_TextOverflow]
    text_rendering: PropertyValue[_TextRendering]
    text_shadow: PropertyValue[_TextShadow]
    text_size_adjust: PropertyValue[_TextSizeAdjust]
    text_spacing_trim: PropertyValue[_TextSpacingTrim]
    text_transform: PropertyValue[_TextTransform]
    text_underline_offset: PropertyValue[_TextUnderlineOffset]
    text_underline_position: PropertyValue[_TextUnderlinePosition]
    text_wrap: PropertyValue[_TextWrap]
    text_wrap_mode: PropertyValue[_TextWrapMode]
    text_wrap_style: PropertyValue[_TextWrapStyle]
    timeline_scope: PropertyValue[_TimelineScope]
    timeline_trigger: PropertyValue[_TimelineTrigger]
    timeline_trigger_activation_range: PropertyValue[
        _TimelineTriggerActivationRange
    ]
    timeline_trigger_activation_range_end: PropertyValue[
        _TimelineTriggerActivationRangeEnd
    ]
    timeline_trigger_activation_range_start: PropertyValue[
        _TimelineTriggerActivationRangeStart
    ]
    timeline_trigger_active_range: PropertyValue[_TimelineTriggerActiveRange]
    timeline_trigger_active_range_end: PropertyValue[
        _TimelineTriggerActiveRangeEnd
    ]
    timeline_trigger_active_range_start: PropertyValue[
        _TimelineTriggerActiveRangeStart
    ]
    timeline_trigger_name: PropertyValue[_TimelineTriggerName]
    timeline_trigger_source: PropertyValue[_TimelineTriggerSource]
    top: PropertyValue[_Top]
    touch_action: PropertyValue[_TouchAction]
    transform: PropertyValue[_Transform]
    transform_box: PropertyValue[_TransformBox]
    transform_origin: PropertyValue[_TransformOrigin]
    transform_style: PropertyValue[_TransformStyle]
    transition: PropertyValue[_Transition]
    transition_behavior: PropertyValue[_TransitionBehavior]
    transition_delay: PropertyValue[_TransitionDelay]
    transition_duration: PropertyValue[_TransitionDuration]
    transition_property: PropertyValue[_TransitionProperty]
    transition_timing_function: PropertyValue[_TransitionTimingFunction]
    translate: PropertyValue[_Translate]
    trigger_scope: PropertyValue[_TriggerScope]
    types: PropertyValue[_Types]
    unicode_bidi: PropertyValue[_UnicodeBidi]
    unicode_range: PropertyValue[_UnicodeRange]
    user_select: PropertyValue[_UserSelect]
    vector_effect: PropertyValue[_VectorEffect]
    vertical_align: PropertyValue[_VerticalAlign]
    view_timeline: PropertyValue[_ViewTimeline]
    view_timeline_axis: PropertyValue[_ViewTimelineAxis]
    view_timeline_inset: PropertyValue[_ViewTimelineInset]
    view_timeline_name: PropertyValue[_ViewTimelineName]
    view_transition_class: PropertyValue[_ViewTransitionClass]
    view_transition_name: PropertyValue[_ViewTransitionName]
    view_transition_scope: PropertyValue[_ViewTransitionScope]
    visibility: PropertyValue[_Visibility]
    white_space: PropertyValue[_WhiteSpace]
    white_space_collapse: PropertyValue[_WhiteSpaceCollapse]
    widows: PropertyValue[_Widows]
    width: PropertyValue[_Width]
    will_change: PropertyValue[_WillChange]
    window_drag: PropertyValue[_WindowDrag]
    word_break: PropertyValue[_WordBreak]
    word_spacing: PropertyValue[_WordSpacing]
    word_wrap: PropertyValue[_WordWrap]
    writing_mode: PropertyValue[_WritingMode]
    x: PropertyValue[_X]
    y: PropertyValue[_Y]
    z_index: PropertyValue[_ZIndex]
    zoom: PropertyValue[_Zoom]
    _moz_appearance: PropertyValue[_MozAppearance]
    _moz_binding: PropertyValue[_MozBinding]
    _moz_border_bottom_colors: PropertyValue[_MozBorderBottomColors]
    _moz_border_left_colors: PropertyValue[_MozBorderLeftColors]
    _moz_border_right_colors: PropertyValue[_MozBorderRightColors]
    _moz_border_top_colors: PropertyValue[_MozBorderTopColors]
    _moz_context_properties: PropertyValue[_MozContextProperties]
    _moz_float_edge: PropertyValue[_MozFloatEdge]
    _moz_force_broken_image_icon: PropertyValue[_MozForceBrokenImageIcon]
    _moz_orient: PropertyValue[_MozOrient]
    _moz_outline_radius: PropertyValue[_MozOutlineRadius]
    _moz_outline_radius_bottomleft: PropertyValue[_MozOutlineRadiusBottomleft]
    _moz_outline_radius_bottomright: PropertyValue[
        _MozOutlineRadiusBottomright
    ]
    _moz_outline_radius_topleft: PropertyValue[_MozOutlineRadiusTopleft]
    _moz_outline_radius_topright: PropertyValue[_MozOutlineRadiusTopright]
    _moz_stack_sizing: PropertyValue[_MozStackSizing]
    _moz_text_blink: PropertyValue[_MozTextBlink]
    _moz_user_focus: PropertyValue[_MozUserFocus]
    _moz_user_input: PropertyValue[_MozUserInput]
    _moz_user_modify: PropertyValue[_MozUserModify]
    _moz_window_dragging: PropertyValue[_MozWindowDragging]
    _moz_window_shadow: PropertyValue[_MozWindowShadow]
    _ms_accelerator: PropertyValue[_MsAccelerator]
    _ms_block_progression: PropertyValue[_MsBlockProgression]
    _ms_content_zoom_chaining: PropertyValue[_MsContentZoomChaining]
    _ms_content_zoom_limit: PropertyValue[_MsContentZoomLimit]
    _ms_content_zoom_limit_max: PropertyValue[_MsContentZoomLimitMax]
    _ms_content_zoom_limit_min: PropertyValue[_MsContentZoomLimitMin]
    _ms_content_zoom_snap: PropertyValue[_MsContentZoomSnap]
    _ms_content_zoom_snap_points: PropertyValue[_MsContentZoomSnapPoints]
    _ms_content_zoom_snap_type: PropertyValue[_MsContentZoomSnapType]
    _ms_content_zooming: PropertyValue[_MsContentZooming]
    _ms_filter: PropertyValue[_MsFilter]
    _ms_flow_from: PropertyValue[_MsFlowFrom]
    _ms_flow_into: PropertyValue[_MsFlowInto]
    _ms_grid_columns: PropertyValue[_MsGridColumns]
    _ms_grid_rows: PropertyValue[_MsGridRows]
    _ms_high_contrast_adjust: PropertyValue[_MsHighContrastAdjust]
    _ms_hyphenate_limit_chars: PropertyValue[_MsHyphenateLimitChars]
    _ms_hyphenate_limit_lines: PropertyValue[_MsHyphenateLimitLines]
    _ms_hyphenate_limit_zone: PropertyValue[_MsHyphenateLimitZone]
    _ms_ime_align: PropertyValue[_MsImeAlign]
    _ms_overflow_style: PropertyValue[_MsOverflowStyle]
    _ms_scroll_chaining: PropertyValue[_MsScrollChaining]
    _ms_scroll_limit: PropertyValue[_MsScrollLimit]
    _ms_scroll_limit_x_max: PropertyValue[_MsScrollLimitXMax]
    _ms_scroll_limit_x_min: PropertyValue[_MsScrollLimitXMin]
    _ms_scroll_limit_y_max: PropertyValue[_MsScrollLimitYMax]
    _ms_scroll_limit_y_min: PropertyValue[_MsScrollLimitYMin]
    _ms_scroll_rails: PropertyValue[_MsScrollRails]
    _ms_scroll_snap_points_x: PropertyValue[_MsScrollSnapPointsX]
    _ms_scroll_snap_points_y: PropertyValue[_MsScrollSnapPointsY]
    _ms_scroll_snap_type: PropertyValue[_MsScrollSnapType]
    _ms_scroll_snap_x: PropertyValue[_MsScrollSnapX]
    _ms_scroll_snap_y: PropertyValue[_MsScrollSnapY]
    _ms_scroll_translation: PropertyValue[_MsScrollTranslation]
    _ms_scrollbar_3dlight_color: PropertyValue[_MsScrollbar3dlightColor]
    _ms_scrollbar_arrow_color: PropertyValue[_MsScrollbarArrowColor]
    _ms_scrollbar_base_color: PropertyValue[_MsScrollbarBaseColor]
    _ms_scrollbar_darkshadow_color: PropertyValue[_MsScrollbarDarkshadowColor]
    _ms_scrollbar_face_color: PropertyValue[_MsScrollbarFaceColor]
    _ms_scrollbar_highlight_color: PropertyValue[_MsScrollbarHighlightColor]
    _ms_scrollbar_shadow_color: PropertyValue[_MsScrollbarShadowColor]
    _ms_scrollbar_track_color: PropertyValue[_MsScrollbarTrackColor]
    _ms_text_autospace: PropertyValue[_MsTextAutospace]
    _ms_touch_select: PropertyValue[_MsTouchSelect]
    _ms_user_select: PropertyValue[_MsUserSelect]
    _ms_wrap_flow: PropertyValue[_MsWrapFlow]
    _ms_wrap_margin: PropertyValue[_MsWrapMargin]
    _ms_wrap_through: PropertyValue[_MsWrapThrough]
    _webkit_appearance: PropertyValue[_WebkitAppearance]
    _webkit_border_after: PropertyValue[_WebkitBorderAfter]
    _webkit_border_after_color: PropertyValue[_WebkitBorderAfterColor]
    _webkit_border_after_style: PropertyValue[_WebkitBorderAfterStyle]
    _webkit_border_after_width: PropertyValue[_WebkitBorderAfterWidth]
    _webkit_border_before: PropertyValue[_WebkitBorderBefore]
    _webkit_border_before_color: PropertyValue[_WebkitBorderBeforeColor]
    _webkit_border_before_style: PropertyValue[_WebkitBorderBeforeStyle]
    _webkit_border_before_width: PropertyValue[_WebkitBorderBeforeWidth]
    _webkit_border_end: PropertyValue[_WebkitBorderEnd]
    _webkit_border_end_color: PropertyValue[_WebkitBorderEndColor]
    _webkit_border_end_style: PropertyValue[_WebkitBorderEndStyle]
    _webkit_border_end_width: PropertyValue[_WebkitBorderEndWidth]
    _webkit_border_start: PropertyValue[_WebkitBorderStart]
    _webkit_border_start_color: PropertyValue[_WebkitBorderStartColor]
    _webkit_border_start_style: PropertyValue[_WebkitBorderStartStyle]
    _webkit_border_start_width: PropertyValue[_WebkitBorderStartWidth]
    _webkit_box_reflect: PropertyValue[_WebkitBoxReflect]
    _webkit_line_clamp: PropertyValue[_WebkitLineClamp]
    _webkit_mask: PropertyValue[_WebkitMask]
    _webkit_mask_attachment: PropertyValue[_WebkitMaskAttachment]
    _webkit_mask_clip: PropertyValue[_WebkitMaskClip]
    _webkit_mask_composite: PropertyValue[_WebkitMaskComposite]
    _webkit_mask_image: PropertyValue[_WebkitMaskImage]
    _webkit_mask_origin: PropertyValue[_WebkitMaskOrigin]
    _webkit_mask_position: PropertyValue[_WebkitMaskPosition]
    _webkit_mask_position_x: PropertyValue[_WebkitMaskPositionX]
    _webkit_mask_position_y: PropertyValue[_WebkitMaskPositionY]
    _webkit_mask_repeat: PropertyValue[_WebkitMaskRepeat]
    _webkit_mask_repeat_x: PropertyValue[_WebkitMaskRepeatX]
    _webkit_mask_repeat_y: PropertyValue[_WebkitMaskRepeatY]
    _webkit_mask_size: PropertyValue[_WebkitMaskSize]
    _webkit_overflow_scrolling: PropertyValue[_WebkitOverflowScrolling]
    _webkit_tap_highlight_color: PropertyValue[_WebkitTapHighlightColor]
    _webkit_text_fill_color: PropertyValue[_WebkitTextFillColor]
    _webkit_text_stroke: PropertyValue[_WebkitTextStroke]
    _webkit_text_stroke_color: PropertyValue[_WebkitTextStrokeColor]
    _webkit_text_stroke_width: PropertyValue[_WebkitTextStrokeWidth]
    _webkit_touch_callout: PropertyValue[_WebkitTouchCallout]
    _webkit_user_modify: PropertyValue[_WebkitUserModify]
    _webkit_user_select: PropertyValue[_WebkitUserSelect]
