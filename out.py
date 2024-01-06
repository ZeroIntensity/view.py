DownloadType: TypeAlias = str | Present
HrefType: TypeAlias = str
HreflangType: TypeAlias = str
PingType: TypeAlias = List[str]
ReferrerpolicyType: TypeAlias = Literal["no-referrer", "no-referrer-when-downgrade", "origin", "origin-when-cross-origin", "same-origin", "strict-origin", "strict-origin-when-cross-origin", "unsafe-url"]
RelType: TypeAlias = str
TargetType: TypeAlias = Literal["_self", "_blank", "_parent", "_top"]
TypeType: TypeAlias = str
AltType: TypeAlias = str
CoordsType: TypeAlias = List[int]
ShapeType: TypeAlias = Literal["rect", "circle", "poly", "default"]
AutoplayType: TypeAlias = Present
ControlsType: TypeAlias = Present
ControlslistType: TypeAlias = Literal["nodownload", "nofullscreen", "noremoteplayback"]
CrossoriginType: TypeAlias = Literal["anonymous", "use-credentials"]
DisableremoteplaybackType: TypeAlias = Present
LoopType: TypeAlias = Present
MutedType: TypeAlias = Present
PreloadType: TypeAlias = Literal["none", "metadata", "auto", ""]
SrcType: TypeAlias = str
DirType: TypeAlias = Literal["ltr", "rtl"]
CiteType: TypeAlias = str
OnafterprintType: TypeAlias = Callback
OnbeforeprintType: TypeAlias = Callback
OnbeforeunloadType: TypeAlias = Callback
OnblurType: TypeAlias = Callback
OnerrorType: TypeAlias = Callback
OnfocusType: TypeAlias = Callback
OnhashchangeType: TypeAlias = Callback
OnlanguagechangeType: TypeAlias = Callback
OnloadType: TypeAlias = Callback
OnmessageType: TypeAlias = Callback
OnofflineType: TypeAlias = Callback
OnonlineType: TypeAlias = Callback
OnpopstateType: TypeAlias = Callback
OnredoType: TypeAlias = Callback
OnresizeType: TypeAlias = Callback
OnstorageType: TypeAlias = Callback
OnundoType: TypeAlias = Callback
OnunloadType: TypeAlias = Callback
AutofocusType: TypeAlias = Present
DisabledType: TypeAlias = Present
FormType: TypeAlias = str
FormactionType: TypeAlias = str
FormenctypeType: TypeAlias = str
FormmethodType: TypeAlias = Literal["post", "get", "dialog"]
FormnovalidateType: TypeAlias = Present
FormtargetType: TypeAlias = Literal["_self", "_blank", "_parent", "_top"]
NameType: TypeAlias = str
PopovertargetType: TypeAlias = str
PopovertargetactionType: TypeAlias = Literal["hide", "show", "toggle"]
ValueType: TypeAlias = str
HeightType: TypeAlias = int
WidthType: TypeAlias = int
SpanType: TypeAlias = int
DatetimeType: TypeAlias = str
OpenType: TypeAlias = Present
AutocapitalizeType: TypeAlias = Literal["on", "off", "sentences", "words", "characters"]
AutocompleteType: TypeAlias = Literal["on", "off"]
XmlnsType: TypeAlias = str
AllowType: TypeAlias = str
AllowfullscreenType: TypeAlias = Present
LoadingType: TypeAlias = Literal["eager", "lazy"]
SandboxType: TypeAlias = str
SrcdocType: TypeAlias = str
DecodingType: TypeAlias = Literal["sync", "async", "auto"]
ElementtimingType: TypeAlias = str
FetchpriorityType: TypeAlias = Literal["high", "low", "auto"]
IsmapType: TypeAlias = Present
SizesType: TypeAlias = str
SrcsetType: TypeAlias = str
UsemapType: TypeAlias = str
For_Type: TypeAlias = str
As_Type: TypeAlias = str
ImagesizesType: TypeAlias = str
ImagesrcsetType: TypeAlias = str
IntegrityType: TypeAlias = str
MediaType: TypeAlias = str
TitleType: TypeAlias = str
CharsetType: TypeAlias = str
ContentType: TypeAlias = str
MinType: TypeAlias = int
MaxType: TypeAlias = int
LowType: TypeAlias = int
HighType: TypeAlias = int
OptimumType: TypeAlias = int
DataType: TypeAlias = List[str]
ReversedType: TypeAlias = Present
StartType: TypeAlias = int
LabelType: TypeAlias = str
SelectedType: TypeAlias = Present
Async_Type: TypeAlias = Present
DeferType: TypeAlias = Present
NomoduleType: TypeAlias = Present
NonceType: TypeAlias = str
MultipleType: TypeAlias = Present
RequiredType: TypeAlias = Present
SizeType: TypeAlias = int
ColspanType: TypeAlias = int
HeadersType: TypeAlias = List[str]
RowspanType: TypeAlias = int
ColsType: TypeAlias = int
DirnameType: TypeAlias = str
MaxlengthType: TypeAlias = int
MinlengthType: TypeAlias = int
PlaceholderType: TypeAlias = str
ReadonlyType: TypeAlias = Present
RowsType: TypeAlias = int
SpellcheckType: TypeAlias = Literal["true", "default", "false"]
WrapType: TypeAlias = Literal["hard", "soft", "off"]
AbbrType: TypeAlias = str
ScopeType: TypeAlias = Literal["row", "col", "rowgroup", "colgroup"]
DefaultType: TypeAlias = Present
KindType: TypeAlias = Literal["subtitles", "captions", "descriptions", "chapters", "metadata"]
SrclangType: TypeAlias = str
PlaysinlineType: TypeAlias = Present
PosterType: TypeAlias = str
Accept_charsetType: TypeAlias = List[str]
Http_equivType: TypeAlias = Literal["content-security-policy", "content-type", "default-style", "x-ua-compatible", "refresh"]
class AComponent(Component):
    '''
    Component class for the `<a>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a
    '''
    TAG_NAME: ClassVar[str] = "a"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['download', 'href', 'hreflang', 'ping', 'referrerpolicy', 'rel', 'target', 'type']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        download: DownloadType | _ImplDefinedType = _ImplDefined,
        href: HrefType | _ImplDefinedType = _ImplDefined,
        hreflang: HreflangType | _ImplDefinedType = _ImplDefined,
        ping: PingType | _ImplDefinedType = _ImplDefined,
        referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
        rel: RelType | _ImplDefinedType = _ImplDefined,
        target: TargetType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._download: DownloadType | _ImplDefinedType = download
        self._href: HrefType | _ImplDefinedType = href
        self._hreflang: HreflangType | _ImplDefinedType = hreflang
        self._ping: PingType | _ImplDefinedType = ping
        self._referrerpolicy: ReferrerpolicyType | _ImplDefinedType = referrerpolicy
        self._rel: RelType | _ImplDefinedType = rel
        self._target: TargetType | _ImplDefinedType = target
        self._type: TypeType | _ImplDefinedType = type

    @property
    def download(self) -> DownloadType | None:
        return _handle_impl_defined(self._download)

    @property
    def href(self) -> HrefType | None:
        return _handle_impl_defined(self._href)

    @property
    def hreflang(self) -> HreflangType | None:
        return _handle_impl_defined(self._hreflang)

    @property
    def ping(self) -> PingType | None:
        return _handle_impl_defined(self._ping)

    @property
    def referrerpolicy(self) -> ReferrerpolicyType | None:
        return _handle_impl_defined(self._referrerpolicy)

    @property
    def rel(self) -> RelType | None:
        return _handle_impl_defined(self._rel)

    @property
    def target(self) -> TargetType | None:
        return _handle_impl_defined(self._target)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

        
class AbbrComponent(Component):
    '''
    Component class for the `<abbr>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/abbr
    '''
    TAG_NAME: ClassVar[str] = "abbr"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class AddressComponent(Component):
    '''
    Component class for the `<address>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address
    '''
    TAG_NAME: ClassVar[str] = "address"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class AreaComponent(Component):
    '''
    Component class for the `<area>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area
    '''
    TAG_NAME: ClassVar[str] = "area"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['alt', 'coords', 'download', 'href', 'ping', 'referrerpolicy', 'rel', 'shape', 'target']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        alt: AltType | _ImplDefinedType = _ImplDefined,
        coords: CoordsType | _ImplDefinedType = _ImplDefined,
        download: DownloadType | _ImplDefinedType = _ImplDefined,
        href: HrefType | _ImplDefinedType = _ImplDefined,
        ping: PingType | _ImplDefinedType = _ImplDefined,
        referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
        rel: RelType | _ImplDefinedType = _ImplDefined,
        shape: ShapeType | _ImplDefinedType = _ImplDefined,
        target: TargetType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._alt: AltType | _ImplDefinedType = alt
        self._coords: CoordsType | _ImplDefinedType = coords
        self._download: DownloadType | _ImplDefinedType = download
        self._href: HrefType | _ImplDefinedType = href
        self._ping: PingType | _ImplDefinedType = ping
        self._referrerpolicy: ReferrerpolicyType | _ImplDefinedType = referrerpolicy
        self._rel: RelType | _ImplDefinedType = rel
        self._shape: ShapeType | _ImplDefinedType = shape
        self._target: TargetType | _ImplDefinedType = target

    @property
    def alt(self) -> AltType | None:
        return _handle_impl_defined(self._alt)

    @property
    def coords(self) -> CoordsType | None:
        return _handle_impl_defined(self._coords)

    @property
    def download(self) -> DownloadType | None:
        return _handle_impl_defined(self._download)

    @property
    def href(self) -> HrefType | None:
        return _handle_impl_defined(self._href)

    @property
    def ping(self) -> PingType | None:
        return _handle_impl_defined(self._ping)

    @property
    def referrerpolicy(self) -> ReferrerpolicyType | None:
        return _handle_impl_defined(self._referrerpolicy)

    @property
    def rel(self) -> RelType | None:
        return _handle_impl_defined(self._rel)

    @property
    def shape(self) -> ShapeType | None:
        return _handle_impl_defined(self._shape)

    @property
    def target(self) -> TargetType | None:
        return _handle_impl_defined(self._target)

        
class ArticleComponent(Component):
    '''
    Component class for the `<article>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/article
    '''
    TAG_NAME: ClassVar[str] = "article"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class AsideComponent(Component):
    '''
    Component class for the `<aside>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/aside
    '''
    TAG_NAME: ClassVar[str] = "aside"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class AudioComponent(Component):
    '''
    Component class for the `<audio>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio
    '''
    TAG_NAME: ClassVar[str] = "audio"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['autoplay', 'controls', 'crossorigin', 'disableremoteplayback', 'loop', 'muted', 'preload', 'src']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        autoplay: AutoplayType | _ImplDefinedType = _ImplDefined,
        controls: ControlsType | _ImplDefinedType = _ImplDefined,
        crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
        disableremoteplayback: DisableremoteplaybackType | _ImplDefinedType = _ImplDefined,
        loop: LoopType | _ImplDefinedType = _ImplDefined,
        muted: MutedType | _ImplDefinedType = _ImplDefined,
        preload: PreloadType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._autoplay: AutoplayType | _ImplDefinedType = autoplay
        self._controls: ControlsType | _ImplDefinedType = controls
        self._crossorigin: CrossoriginType | _ImplDefinedType = crossorigin
        self._disableremoteplayback: DisableremoteplaybackType | _ImplDefinedType = disableremoteplayback
        self._loop: LoopType | _ImplDefinedType = loop
        self._muted: MutedType | _ImplDefinedType = muted
        self._preload: PreloadType | _ImplDefinedType = preload
        self._src: SrcType | _ImplDefinedType = src

    @property
    def autoplay(self) -> AutoplayType | None:
        return _handle_impl_defined(self._autoplay)

    @property
    def controls(self) -> ControlsType | None:
        return _handle_impl_defined(self._controls)

    @property
    def crossorigin(self) -> CrossoriginType | None:
        return _handle_impl_defined(self._crossorigin)

    @property
    def disableremoteplayback(self) -> DisableremoteplaybackType | None:
        return _handle_impl_defined(self._disableremoteplayback)

    @property
    def loop(self) -> LoopType | None:
        return _handle_impl_defined(self._loop)

    @property
    def muted(self) -> MutedType | None:
        return _handle_impl_defined(self._muted)

    @property
    def preload(self) -> PreloadType | None:
        return _handle_impl_defined(self._preload)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

        
class BComponent(Component):
    '''
    Component class for the `<b>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/b
    '''
    TAG_NAME: ClassVar[str] = "b"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class BaseComponent(Component):
    '''
    Component class for the `<base>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base
    '''
    TAG_NAME: ClassVar[str] = "base"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['href', 'target']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        href: HrefType | _ImplDefinedType = _ImplDefined,
        target: TargetType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._href: HrefType | _ImplDefinedType = href
        self._target: TargetType | _ImplDefinedType = target

    @property
    def href(self) -> HrefType | None:
        return _handle_impl_defined(self._href)

    @property
    def target(self) -> TargetType | None:
        return _handle_impl_defined(self._target)

        
class BdiComponent(Component):
    '''
    Component class for the `<bdi>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdi
    '''
    TAG_NAME: ClassVar[str] = "bdi"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class BdoComponent(Component):
    '''
    Component class for the `<bdo>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdo
    '''
    TAG_NAME: ClassVar[str] = "bdo"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['dir']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        dir: DirType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._dir: DirType | _ImplDefinedType = dir

    @property
    def dir(self) -> DirType | None:
        return _handle_impl_defined(self._dir)

        
class BlockquoteComponent(Component):
    '''
    Component class for the `<blockquote>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blockquote
    '''
    TAG_NAME: ClassVar[str] = "blockquote"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['cite']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        cite: CiteType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._cite: CiteType | _ImplDefinedType = cite

    @property
    def cite(self) -> CiteType | None:
        return _handle_impl_defined(self._cite)

        
class BodyComponent(Component):
    '''
    Component class for the `<body>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body
    '''
    TAG_NAME: ClassVar[str] = "body"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['onafterprint', 'onbeforeprint', 'onbeforeunload', 'onblur', 'onerror', 'onfocus', 'onhashchange', 'onlanguagechange', 'onload', 'onmessage', 'onoffline', 'ononline', 'onpopstate', 'onredo', 'onresize', 'onstorage', 'onundo', 'onunload']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        onafterprint: OnafterprintType | _ImplDefinedType = _ImplDefined,
        onbeforeprint: OnbeforeprintType | _ImplDefinedType = _ImplDefined,
        onbeforeunload: OnbeforeunloadType | _ImplDefinedType = _ImplDefined,
        onblur: OnblurType | _ImplDefinedType = _ImplDefined,
        onerror: OnerrorType | _ImplDefinedType = _ImplDefined,
        onfocus: OnfocusType | _ImplDefinedType = _ImplDefined,
        onhashchange: OnhashchangeType | _ImplDefinedType = _ImplDefined,
        onlanguagechange: OnlanguagechangeType | _ImplDefinedType = _ImplDefined,
        onload: OnloadType | _ImplDefinedType = _ImplDefined,
        onmessage: OnmessageType | _ImplDefinedType = _ImplDefined,
        onoffline: OnofflineType | _ImplDefinedType = _ImplDefined,
        ononline: OnonlineType | _ImplDefinedType = _ImplDefined,
        onpopstate: OnpopstateType | _ImplDefinedType = _ImplDefined,
        onredo: OnredoType | _ImplDefinedType = _ImplDefined,
        onresize: OnresizeType | _ImplDefinedType = _ImplDefined,
        onstorage: OnstorageType | _ImplDefinedType = _ImplDefined,
        onundo: OnundoType | _ImplDefinedType = _ImplDefined,
        onunload: OnunloadType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._onafterprint: OnafterprintType | _ImplDefinedType = onafterprint
        self._onbeforeprint: OnbeforeprintType | _ImplDefinedType = onbeforeprint
        self._onbeforeunload: OnbeforeunloadType | _ImplDefinedType = onbeforeunload
        self._onblur: OnblurType | _ImplDefinedType = onblur
        self._onerror: OnerrorType | _ImplDefinedType = onerror
        self._onfocus: OnfocusType | _ImplDefinedType = onfocus
        self._onhashchange: OnhashchangeType | _ImplDefinedType = onhashchange
        self._onlanguagechange: OnlanguagechangeType | _ImplDefinedType = onlanguagechange
        self._onload: OnloadType | _ImplDefinedType = onload
        self._onmessage: OnmessageType | _ImplDefinedType = onmessage
        self._onoffline: OnofflineType | _ImplDefinedType = onoffline
        self._ononline: OnonlineType | _ImplDefinedType = ononline
        self._onpopstate: OnpopstateType | _ImplDefinedType = onpopstate
        self._onredo: OnredoType | _ImplDefinedType = onredo
        self._onresize: OnresizeType | _ImplDefinedType = onresize
        self._onstorage: OnstorageType | _ImplDefinedType = onstorage
        self._onundo: OnundoType | _ImplDefinedType = onundo
        self._onunload: OnunloadType | _ImplDefinedType = onunload

    @property
    def onafterprint(self) -> OnafterprintType | None:
        return _handle_impl_defined(self._onafterprint)

    @property
    def onbeforeprint(self) -> OnbeforeprintType | None:
        return _handle_impl_defined(self._onbeforeprint)

    @property
    def onbeforeunload(self) -> OnbeforeunloadType | None:
        return _handle_impl_defined(self._onbeforeunload)

    @property
    def onblur(self) -> OnblurType | None:
        return _handle_impl_defined(self._onblur)

    @property
    def onerror(self) -> OnerrorType | None:
        return _handle_impl_defined(self._onerror)

    @property
    def onfocus(self) -> OnfocusType | None:
        return _handle_impl_defined(self._onfocus)

    @property
    def onhashchange(self) -> OnhashchangeType | None:
        return _handle_impl_defined(self._onhashchange)

    @property
    def onlanguagechange(self) -> OnlanguagechangeType | None:
        return _handle_impl_defined(self._onlanguagechange)

    @property
    def onload(self) -> OnloadType | None:
        return _handle_impl_defined(self._onload)

    @property
    def onmessage(self) -> OnmessageType | None:
        return _handle_impl_defined(self._onmessage)

    @property
    def onoffline(self) -> OnofflineType | None:
        return _handle_impl_defined(self._onoffline)

    @property
    def ononline(self) -> OnonlineType | None:
        return _handle_impl_defined(self._ononline)

    @property
    def onpopstate(self) -> OnpopstateType | None:
        return _handle_impl_defined(self._onpopstate)

    @property
    def onredo(self) -> OnredoType | None:
        return _handle_impl_defined(self._onredo)

    @property
    def onresize(self) -> OnresizeType | None:
        return _handle_impl_defined(self._onresize)

    @property
    def onstorage(self) -> OnstorageType | None:
        return _handle_impl_defined(self._onstorage)

    @property
    def onundo(self) -> OnundoType | None:
        return _handle_impl_defined(self._onundo)

    @property
    def onunload(self) -> OnunloadType | None:
        return _handle_impl_defined(self._onunload)

        
class BrComponent(Component):
    '''
    Component class for the `<br>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/br
    '''
    TAG_NAME: ClassVar[str] = "br"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class ButtonComponent(Component):
    '''
    Component class for the `<button>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button
    '''
    TAG_NAME: ClassVar[str] = "button"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['autofocus', 'disabled', 'form', 'formaction', 'formenctype', 'formmethod', 'formnovalidate', 'formtarget', 'name', 'popovertarget', 'popovertargetaction', 'type', 'value']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        autofocus: AutofocusType | _ImplDefinedType = _ImplDefined,
        disabled: DisabledType | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
        formaction: FormactionType | _ImplDefinedType = _ImplDefined,
        formenctype: FormenctypeType | _ImplDefinedType = _ImplDefined,
        formmethod: FormmethodType | _ImplDefinedType = _ImplDefined,
        formnovalidate: FormnovalidateType | _ImplDefinedType = _ImplDefined,
        formtarget: FormtargetType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
        popovertarget: PopovertargetType | _ImplDefinedType = _ImplDefined,
        popovertargetaction: PopovertargetactionType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
        value: ValueType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._autofocus: AutofocusType | _ImplDefinedType = autofocus
        self._disabled: DisabledType | _ImplDefinedType = disabled
        self._form: FormType | _ImplDefinedType = form
        self._formaction: FormactionType | _ImplDefinedType = formaction
        self._formenctype: FormenctypeType | _ImplDefinedType = formenctype
        self._formmethod: FormmethodType | _ImplDefinedType = formmethod
        self._formnovalidate: FormnovalidateType | _ImplDefinedType = formnovalidate
        self._formtarget: FormtargetType | _ImplDefinedType = formtarget
        self._name: NameType | _ImplDefinedType = name
        self._popovertarget: PopovertargetType | _ImplDefinedType = popovertarget
        self._popovertargetaction: PopovertargetactionType | _ImplDefinedType = popovertargetaction
        self._type: TypeType | _ImplDefinedType = type
        self._value: ValueType | _ImplDefinedType = value

    @property
    def autofocus(self) -> AutofocusType | None:
        return _handle_impl_defined(self._autofocus)

    @property
    def disabled(self) -> DisabledType | None:
        return _handle_impl_defined(self._disabled)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

    @property
    def formaction(self) -> FormactionType | None:
        return _handle_impl_defined(self._formaction)

    @property
    def formenctype(self) -> FormenctypeType | None:
        return _handle_impl_defined(self._formenctype)

    @property
    def formmethod(self) -> FormmethodType | None:
        return _handle_impl_defined(self._formmethod)

    @property
    def formnovalidate(self) -> FormnovalidateType | None:
        return _handle_impl_defined(self._formnovalidate)

    @property
    def formtarget(self) -> FormtargetType | None:
        return _handle_impl_defined(self._formtarget)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

    @property
    def popovertarget(self) -> PopovertargetType | None:
        return _handle_impl_defined(self._popovertarget)

    @property
    def popovertargetaction(self) -> PopovertargetactionType | None:
        return _handle_impl_defined(self._popovertargetaction)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

    @property
    def value(self) -> ValueType | None:
        return _handle_impl_defined(self._value)

        
class CanvasComponent(Component):
    '''
    Component class for the `<canvas>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas
    '''
    TAG_NAME: ClassVar[str] = "canvas"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['height', 'width']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._height: HeightType | _ImplDefinedType = height
        self._width: WidthType | _ImplDefinedType = width

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

        
class CaptionComponent(Component):
    '''
    Component class for the `<caption>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/caption
    '''
    TAG_NAME: ClassVar[str] = "caption"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class CiteComponent(Component):
    '''
    Component class for the `<cite>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/cite
    '''
    TAG_NAME: ClassVar[str] = "cite"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class CodeComponent(Component):
    '''
    Component class for the `<code>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/code
    '''
    TAG_NAME: ClassVar[str] = "code"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class ColComponent(Component):
    '''
    Component class for the `<col>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/col
    '''
    TAG_NAME: ClassVar[str] = "col"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['span']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        span: SpanType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._span: SpanType | _ImplDefinedType = span

    @property
    def span(self) -> SpanType | None:
        return _handle_impl_defined(self._span)

        
class ColgroupComponent(Component):
    '''
    Component class for the `<colgroup>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup
    '''
    TAG_NAME: ClassVar[str] = "colgroup"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['span']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        span: SpanType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._span: SpanType | _ImplDefinedType = span

    @property
    def span(self) -> SpanType | None:
        return _handle_impl_defined(self._span)

        
class DataComponent(Component):
    '''
    Component class for the `<data>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data
    '''
    TAG_NAME: ClassVar[str] = "data"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['value']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        value: ValueType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._value: ValueType | _ImplDefinedType = value

    @property
    def value(self) -> ValueType | None:
        return _handle_impl_defined(self._value)

        
class DatalistComponent(Component):
    '''
    Component class for the `<datalist>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/datalist
    '''
    TAG_NAME: ClassVar[str] = "datalist"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class DdComponent(Component):
    '''
    Component class for the `<dd>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dd
    '''
    TAG_NAME: ClassVar[str] = "dd"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class Del_Component(Component):
    '''
    Component class for the `<del_>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del
    '''
    TAG_NAME: ClassVar[str] = "del_"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['cite', 'datetime']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        cite: CiteType | _ImplDefinedType = _ImplDefined,
        datetime: DatetimeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._cite: CiteType | _ImplDefinedType = cite
        self._datetime: DatetimeType | _ImplDefinedType = datetime

    @property
    def cite(self) -> CiteType | None:
        return _handle_impl_defined(self._cite)

    @property
    def datetime(self) -> DatetimeType | None:
        return _handle_impl_defined(self._datetime)

        
class DetailsComponent(Component):
    '''
    Component class for the `<details>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details
    '''
    TAG_NAME: ClassVar[str] = "details"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['open']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        open: OpenType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._open: OpenType | _ImplDefinedType = open

    @property
    def open(self) -> OpenType | None:
        return _handle_impl_defined(self._open)

        
class DfnComponent(Component):
    '''
    Component class for the `<dfn>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dfn
    '''
    TAG_NAME: ClassVar[str] = "dfn"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class DialogComponent(Component):
    '''
    Component class for the `<dialog>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog
    '''
    TAG_NAME: ClassVar[str] = "dialog"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['open']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        open: OpenType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._open: OpenType | _ImplDefinedType = open

    @property
    def open(self) -> OpenType | None:
        return _handle_impl_defined(self._open)

        
class DivComponent(Component):
    '''
    Component class for the `<div>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div
    '''
    TAG_NAME: ClassVar[str] = "div"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class DlComponent(Component):
    '''
    Component class for the `<dl>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl
    '''
    TAG_NAME: ClassVar[str] = "dl"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class DtComponent(Component):
    '''
    Component class for the `<dt>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dt
    '''
    TAG_NAME: ClassVar[str] = "dt"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class EmComponent(Component):
    '''
    Component class for the `<em>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/em
    '''
    TAG_NAME: ClassVar[str] = "em"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class EmbedComponent(Component):
    '''
    Component class for the `<embed>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed
    '''
    TAG_NAME: ClassVar[str] = "embed"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['height', 'src', 'type', 'width']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._height: HeightType | _ImplDefinedType = height
        self._src: SrcType | _ImplDefinedType = src
        self._type: TypeType | _ImplDefinedType = type
        self._width: WidthType | _ImplDefinedType = width

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

        
class FieldsetComponent(Component):
    '''
    Component class for the `<fieldset>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset
    '''
    TAG_NAME: ClassVar[str] = "fieldset"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['disabled', 'form', 'name']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        disabled: DisabledType | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._disabled: DisabledType | _ImplDefinedType = disabled
        self._form: FormType | _ImplDefinedType = form
        self._name: NameType | _ImplDefinedType = name

    @property
    def disabled(self) -> DisabledType | None:
        return _handle_impl_defined(self._disabled)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

        
class FigcaptionComponent(Component):
    '''
    Component class for the `<figcaption>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figcaption
    '''
    TAG_NAME: ClassVar[str] = "figcaption"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class FigureComponent(Component):
    '''
    Component class for the `<figure>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figure
    '''
    TAG_NAME: ClassVar[str] = "figure"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class FooterComponent(Component):
    '''
    Component class for the `<footer>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/footer
    '''
    TAG_NAME: ClassVar[str] = "footer"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class FormComponent(Component):
    '''
    Component class for the `<form>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form
    '''
    TAG_NAME: ClassVar[str] = "form"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['accept_charset', 'autocapitalize', 'autocomplete', 'name', 'rel']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        accept_charset: Accept_charsetType | _ImplDefinedType = _ImplDefined,
        autocapitalize: AutocapitalizeType | _ImplDefinedType = _ImplDefined,
        autocomplete: AutocompleteType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
        rel: RelType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._accept_charset: Accept_charsetType | _ImplDefinedType = accept_charset
        self._autocapitalize: AutocapitalizeType | _ImplDefinedType = autocapitalize
        self._autocomplete: AutocompleteType | _ImplDefinedType = autocomplete
        self._name: NameType | _ImplDefinedType = name
        self._rel: RelType | _ImplDefinedType = rel

    @property
    def accept_charset(self) -> Accept_charsetType | None:
        return _handle_impl_defined(self._accept_charset)

    @property
    def autocapitalize(self) -> AutocapitalizeType | None:
        return _handle_impl_defined(self._autocapitalize)

    @property
    def autocomplete(self) -> AutocompleteType | None:
        return _handle_impl_defined(self._autocomplete)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

    @property
    def rel(self) -> RelType | None:
        return _handle_impl_defined(self._rel)

        
class H1Component(Component):
    '''
    Component class for the `<h1>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Heading_Elements
    '''
    TAG_NAME: ClassVar[str] = "h1"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class HeadComponent(Component):
    '''
    Component class for the `<head>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/head
    '''
    TAG_NAME: ClassVar[str] = "head"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class HeaderComponent(Component):
    '''
    Component class for the `<header>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/header
    '''
    TAG_NAME: ClassVar[str] = "header"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class HgroupComponent(Component):
    '''
    Component class for the `<hgroup>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hgroup
    '''
    TAG_NAME: ClassVar[str] = "hgroup"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class HrComponent(Component):
    '''
    Component class for the `<hr>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hr
    '''
    TAG_NAME: ClassVar[str] = "hr"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class HtmlComponent(Component):
    '''
    Component class for the `<html>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/html
    '''
    TAG_NAME: ClassVar[str] = "html"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['xmlns']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        xmlns: XmlnsType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._xmlns: XmlnsType | _ImplDefinedType = xmlns

    @property
    def xmlns(self) -> XmlnsType | None:
        return _handle_impl_defined(self._xmlns)

        
class IComponent(Component):
    '''
    Component class for the `<i>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/i
    '''
    TAG_NAME: ClassVar[str] = "i"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class IframeComponent(Component):
    '''
    Component class for the `<iframe>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe
    '''
    TAG_NAME: ClassVar[str] = "iframe"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['allow', 'allowfullscreen', 'height', 'loading', 'name', 'referrerpolicy', 'sandbox', 'src', 'srcdoc', 'width']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        allow: AllowType | _ImplDefinedType = _ImplDefined,
        allowfullscreen: AllowfullscreenType | _ImplDefinedType = _ImplDefined,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        loading: LoadingType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
        referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
        sandbox: SandboxType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        srcdoc: SrcdocType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._allow: AllowType | _ImplDefinedType = allow
        self._allowfullscreen: AllowfullscreenType | _ImplDefinedType = allowfullscreen
        self._height: HeightType | _ImplDefinedType = height
        self._loading: LoadingType | _ImplDefinedType = loading
        self._name: NameType | _ImplDefinedType = name
        self._referrerpolicy: ReferrerpolicyType | _ImplDefinedType = referrerpolicy
        self._sandbox: SandboxType | _ImplDefinedType = sandbox
        self._src: SrcType | _ImplDefinedType = src
        self._srcdoc: SrcdocType | _ImplDefinedType = srcdoc
        self._width: WidthType | _ImplDefinedType = width

    @property
    def allow(self) -> AllowType | None:
        return _handle_impl_defined(self._allow)

    @property
    def allowfullscreen(self) -> AllowfullscreenType | None:
        return _handle_impl_defined(self._allowfullscreen)

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def loading(self) -> LoadingType | None:
        return _handle_impl_defined(self._loading)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

    @property
    def referrerpolicy(self) -> ReferrerpolicyType | None:
        return _handle_impl_defined(self._referrerpolicy)

    @property
    def sandbox(self) -> SandboxType | None:
        return _handle_impl_defined(self._sandbox)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def srcdoc(self) -> SrcdocType | None:
        return _handle_impl_defined(self._srcdoc)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

        
class ImgComponent(Component):
    '''
    Component class for the `<img>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img
    '''
    TAG_NAME: ClassVar[str] = "img"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['alt', 'crossorigin', 'decoding', 'elementtiming', 'fetchpriority', 'height', 'ismap', 'loading', 'referrerpolicy', 'sizes', 'src', 'srcset', 'width', 'usemap']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        alt: AltType | _ImplDefinedType = _ImplDefined,
        crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
        decoding: DecodingType | _ImplDefinedType = _ImplDefined,
        elementtiming: ElementtimingType | _ImplDefinedType = _ImplDefined,
        fetchpriority: FetchpriorityType | _ImplDefinedType = _ImplDefined,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        ismap: IsmapType | _ImplDefinedType = _ImplDefined,
        loading: LoadingType | _ImplDefinedType = _ImplDefined,
        referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
        sizes: SizesType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        srcset: SrcsetType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
        usemap: UsemapType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._alt: AltType | _ImplDefinedType = alt
        self._crossorigin: CrossoriginType | _ImplDefinedType = crossorigin
        self._decoding: DecodingType | _ImplDefinedType = decoding
        self._elementtiming: ElementtimingType | _ImplDefinedType = elementtiming
        self._fetchpriority: FetchpriorityType | _ImplDefinedType = fetchpriority
        self._height: HeightType | _ImplDefinedType = height
        self._ismap: IsmapType | _ImplDefinedType = ismap
        self._loading: LoadingType | _ImplDefinedType = loading
        self._referrerpolicy: ReferrerpolicyType | _ImplDefinedType = referrerpolicy
        self._sizes: SizesType | _ImplDefinedType = sizes
        self._src: SrcType | _ImplDefinedType = src
        self._srcset: SrcsetType | _ImplDefinedType = srcset
        self._width: WidthType | _ImplDefinedType = width
        self._usemap: UsemapType | _ImplDefinedType = usemap

    @property
    def alt(self) -> AltType | None:
        return _handle_impl_defined(self._alt)

    @property
    def crossorigin(self) -> CrossoriginType | None:
        return _handle_impl_defined(self._crossorigin)

    @property
    def decoding(self) -> DecodingType | None:
        return _handle_impl_defined(self._decoding)

    @property
    def elementtiming(self) -> ElementtimingType | None:
        return _handle_impl_defined(self._elementtiming)

    @property
    def fetchpriority(self) -> FetchpriorityType | None:
        return _handle_impl_defined(self._fetchpriority)

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def ismap(self) -> IsmapType | None:
        return _handle_impl_defined(self._ismap)

    @property
    def loading(self) -> LoadingType | None:
        return _handle_impl_defined(self._loading)

    @property
    def referrerpolicy(self) -> ReferrerpolicyType | None:
        return _handle_impl_defined(self._referrerpolicy)

    @property
    def sizes(self) -> SizesType | None:
        return _handle_impl_defined(self._sizes)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def srcset(self) -> SrcsetType | None:
        return _handle_impl_defined(self._srcset)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

    @property
    def usemap(self) -> UsemapType | None:
        return _handle_impl_defined(self._usemap)

        
class InputComponent(Component):
    '''
    Component class for the `<input>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input
    '''
    TAG_NAME: ClassVar[str] = "input"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class InsComponent(Component):
    '''
    Component class for the `<ins>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins
    '''
    TAG_NAME: ClassVar[str] = "ins"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['cite', 'datetime']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        cite: CiteType | _ImplDefinedType = _ImplDefined,
        datetime: DatetimeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._cite: CiteType | _ImplDefinedType = cite
        self._datetime: DatetimeType | _ImplDefinedType = datetime

    @property
    def cite(self) -> CiteType | None:
        return _handle_impl_defined(self._cite)

    @property
    def datetime(self) -> DatetimeType | None:
        return _handle_impl_defined(self._datetime)

        
class KbdComponent(Component):
    '''
    Component class for the `<kbd>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/kbd
    '''
    TAG_NAME: ClassVar[str] = "kbd"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class LabelComponent(Component):
    '''
    Component class for the `<label>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label
    '''
    TAG_NAME: ClassVar[str] = "label"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['for_']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        for_: For_Type | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._for_: For_Type | _ImplDefinedType = for_

    @property
    def for_(self) -> For_Type | None:
        return _handle_impl_defined(self._for_)

        
class LegendComponent(Component):
    '''
    Component class for the `<legend>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/legend
    '''
    TAG_NAME: ClassVar[str] = "legend"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class LiComponent(Component):
    '''
    Component class for the `<li>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li
    '''
    TAG_NAME: ClassVar[str] = "li"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['value']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        value: ValueType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._value: ValueType | _ImplDefinedType = value

    @property
    def value(self) -> ValueType | None:
        return _handle_impl_defined(self._value)

        
class LinkComponent(Component):
    '''
    Component class for the `<link>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link
    '''
    TAG_NAME: ClassVar[str] = "link"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['as_', 'crossorigin', 'fetchpriority', 'href', 'hreflang', 'imagesizes', 'imagesrcset', 'integrity', 'media', 'referrerpolicy', 'rel', 'sizes', 'title', 'type']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        as_: As_Type | _ImplDefinedType = _ImplDefined,
        crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
        fetchpriority: FetchpriorityType | _ImplDefinedType = _ImplDefined,
        href: HrefType | _ImplDefinedType = _ImplDefined,
        hreflang: HreflangType | _ImplDefinedType = _ImplDefined,
        imagesizes: ImagesizesType | _ImplDefinedType = _ImplDefined,
        imagesrcset: ImagesrcsetType | _ImplDefinedType = _ImplDefined,
        integrity: IntegrityType | _ImplDefinedType = _ImplDefined,
        media: MediaType | _ImplDefinedType = _ImplDefined,
        referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
        rel: RelType | _ImplDefinedType = _ImplDefined,
        sizes: SizesType | _ImplDefinedType = _ImplDefined,
        title: TitleType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._as_: As_Type | _ImplDefinedType = as_
        self._crossorigin: CrossoriginType | _ImplDefinedType = crossorigin
        self._fetchpriority: FetchpriorityType | _ImplDefinedType = fetchpriority
        self._href: HrefType | _ImplDefinedType = href
        self._hreflang: HreflangType | _ImplDefinedType = hreflang
        self._imagesizes: ImagesizesType | _ImplDefinedType = imagesizes
        self._imagesrcset: ImagesrcsetType | _ImplDefinedType = imagesrcset
        self._integrity: IntegrityType | _ImplDefinedType = integrity
        self._media: MediaType | _ImplDefinedType = media
        self._referrerpolicy: ReferrerpolicyType | _ImplDefinedType = referrerpolicy
        self._rel: RelType | _ImplDefinedType = rel
        self._sizes: SizesType | _ImplDefinedType = sizes
        self._title: TitleType | _ImplDefinedType = title
        self._type: TypeType | _ImplDefinedType = type

    @property
    def as_(self) -> As_Type | None:
        return _handle_impl_defined(self._as_)

    @property
    def crossorigin(self) -> CrossoriginType | None:
        return _handle_impl_defined(self._crossorigin)

    @property
    def fetchpriority(self) -> FetchpriorityType | None:
        return _handle_impl_defined(self._fetchpriority)

    @property
    def href(self) -> HrefType | None:
        return _handle_impl_defined(self._href)

    @property
    def hreflang(self) -> HreflangType | None:
        return _handle_impl_defined(self._hreflang)

    @property
    def imagesizes(self) -> ImagesizesType | None:
        return _handle_impl_defined(self._imagesizes)

    @property
    def imagesrcset(self) -> ImagesrcsetType | None:
        return _handle_impl_defined(self._imagesrcset)

    @property
    def integrity(self) -> IntegrityType | None:
        return _handle_impl_defined(self._integrity)

    @property
    def media(self) -> MediaType | None:
        return _handle_impl_defined(self._media)

    @property
    def referrerpolicy(self) -> ReferrerpolicyType | None:
        return _handle_impl_defined(self._referrerpolicy)

    @property
    def rel(self) -> RelType | None:
        return _handle_impl_defined(self._rel)

    @property
    def sizes(self) -> SizesType | None:
        return _handle_impl_defined(self._sizes)

    @property
    def title(self) -> TitleType | None:
        return _handle_impl_defined(self._title)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

        
class MainComponent(Component):
    '''
    Component class for the `<main>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/main
    '''
    TAG_NAME: ClassVar[str] = "main"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class MapComponent(Component):
    '''
    Component class for the `<map>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/map
    '''
    TAG_NAME: ClassVar[str] = "map"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['name']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        name: NameType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._name: NameType | _ImplDefinedType = name

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

        
class MarkComponent(Component):
    '''
    Component class for the `<mark>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/mark
    '''
    TAG_NAME: ClassVar[str] = "mark"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class MenuComponent(Component):
    '''
    Component class for the `<menu>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/menu
    '''
    TAG_NAME: ClassVar[str] = "menu"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class MetaComponent(Component):
    '''
    Component class for the `<meta>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta
    '''
    TAG_NAME: ClassVar[str] = "meta"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['charset', 'content', 'http_equiv', 'name']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        charset: CharsetType | _ImplDefinedType = _ImplDefined,
        content: ContentType | _ImplDefinedType = _ImplDefined,
        http_equiv: Http_equivType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._charset: CharsetType | _ImplDefinedType = charset
        self._content: ContentType | _ImplDefinedType = content
        self._http_equiv: Http_equivType | _ImplDefinedType = http_equiv
        self._name: NameType | _ImplDefinedType = name

    @property
    def charset(self) -> CharsetType | None:
        return _handle_impl_defined(self._charset)

    @property
    def content(self) -> ContentType | None:
        return _handle_impl_defined(self._content)

    @property
    def http_equiv(self) -> Http_equivType | None:
        return _handle_impl_defined(self._http_equiv)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

        
class MeterComponent(Component):
    '''
    Component class for the `<meter>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter
    '''
    TAG_NAME: ClassVar[str] = "meter"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['value', 'min', 'max', 'low', 'high', 'optimum', 'form']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        value: ValueType | _ImplDefinedType = _ImplDefined,
        min: MinType | _ImplDefinedType = _ImplDefined,
        max: MaxType | _ImplDefinedType = _ImplDefined,
        low: LowType | _ImplDefinedType = _ImplDefined,
        high: HighType | _ImplDefinedType = _ImplDefined,
        optimum: OptimumType | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._value: ValueType | _ImplDefinedType = value
        self._min: MinType | _ImplDefinedType = min
        self._max: MaxType | _ImplDefinedType = max
        self._low: LowType | _ImplDefinedType = low
        self._high: HighType | _ImplDefinedType = high
        self._optimum: OptimumType | _ImplDefinedType = optimum
        self._form: FormType | _ImplDefinedType = form

    @property
    def value(self) -> ValueType | None:
        return _handle_impl_defined(self._value)

    @property
    def min(self) -> MinType | None:
        return _handle_impl_defined(self._min)

    @property
    def max(self) -> MaxType | None:
        return _handle_impl_defined(self._max)

    @property
    def low(self) -> LowType | None:
        return _handle_impl_defined(self._low)

    @property
    def high(self) -> HighType | None:
        return _handle_impl_defined(self._high)

    @property
    def optimum(self) -> OptimumType | None:
        return _handle_impl_defined(self._optimum)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

        
class NavComponent(Component):
    '''
    Component class for the `<nav>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nav
    '''
    TAG_NAME: ClassVar[str] = "nav"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class NoscriptComponent(Component):
    '''
    Component class for the `<noscript>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/noscript
    '''
    TAG_NAME: ClassVar[str] = "noscript"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class ObjectComponent(Component):
    '''
    Component class for the `<object>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object
    '''
    TAG_NAME: ClassVar[str] = "object"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['data', 'form', 'height', 'name', 'type', 'usemap', 'width']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        data: DataType | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
        usemap: UsemapType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._data: DataType | _ImplDefinedType = data
        self._form: FormType | _ImplDefinedType = form
        self._height: HeightType | _ImplDefinedType = height
        self._name: NameType | _ImplDefinedType = name
        self._type: TypeType | _ImplDefinedType = type
        self._usemap: UsemapType | _ImplDefinedType = usemap
        self._width: WidthType | _ImplDefinedType = width

    @property
    def data(self) -> DataType | None:
        return _handle_impl_defined(self._data)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

    @property
    def usemap(self) -> UsemapType | None:
        return _handle_impl_defined(self._usemap)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

        
class OlComponent(Component):
    '''
    Component class for the `<ol>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol
    '''
    TAG_NAME: ClassVar[str] = "ol"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['reversed', 'start', 'type']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        reversed: ReversedType | _ImplDefinedType = _ImplDefined,
        start: StartType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._reversed: ReversedType | _ImplDefinedType = reversed
        self._start: StartType | _ImplDefinedType = start
        self._type: TypeType | _ImplDefinedType = type

    @property
    def reversed(self) -> ReversedType | None:
        return _handle_impl_defined(self._reversed)

    @property
    def start(self) -> StartType | None:
        return _handle_impl_defined(self._start)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

        
class OptgroupComponent(Component):
    '''
    Component class for the `<optgroup>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup
    '''
    TAG_NAME: ClassVar[str] = "optgroup"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['disabled', 'label']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        disabled: DisabledType | _ImplDefinedType = _ImplDefined,
        label: LabelType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._disabled: DisabledType | _ImplDefinedType = disabled
        self._label: LabelType | _ImplDefinedType = label

    @property
    def disabled(self) -> DisabledType | None:
        return _handle_impl_defined(self._disabled)

    @property
    def label(self) -> LabelType | None:
        return _handle_impl_defined(self._label)

        
class OptionComponent(Component):
    '''
    Component class for the `<option>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option
    '''
    TAG_NAME: ClassVar[str] = "option"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['disabled', 'label', 'selected', 'value']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        disabled: DisabledType | _ImplDefinedType = _ImplDefined,
        label: LabelType | _ImplDefinedType = _ImplDefined,
        selected: SelectedType | _ImplDefinedType = _ImplDefined,
        value: ValueType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._disabled: DisabledType | _ImplDefinedType = disabled
        self._label: LabelType | _ImplDefinedType = label
        self._selected: SelectedType | _ImplDefinedType = selected
        self._value: ValueType | _ImplDefinedType = value

    @property
    def disabled(self) -> DisabledType | None:
        return _handle_impl_defined(self._disabled)

    @property
    def label(self) -> LabelType | None:
        return _handle_impl_defined(self._label)

    @property
    def selected(self) -> SelectedType | None:
        return _handle_impl_defined(self._selected)

    @property
    def value(self) -> ValueType | None:
        return _handle_impl_defined(self._value)

        
class OutputComponent(Component):
    '''
    Component class for the `<output>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output
    '''
    TAG_NAME: ClassVar[str] = "output"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['for_', 'form', 'name']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        for_: For_Type | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._for_: For_Type | _ImplDefinedType = for_
        self._form: FormType | _ImplDefinedType = form
        self._name: NameType | _ImplDefinedType = name

    @property
    def for_(self) -> For_Type | None:
        return _handle_impl_defined(self._for_)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

        
class PComponent(Component):
    '''
    Component class for the `<p>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/p
    '''
    TAG_NAME: ClassVar[str] = "p"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class PictureComponent(Component):
    '''
    Component class for the `<picture>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture
    '''
    TAG_NAME: ClassVar[str] = "picture"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class PreComponent(Component):
    '''
    Component class for the `<pre>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/pre
    '''
    TAG_NAME: ClassVar[str] = "pre"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class ProgressComponent(Component):
    '''
    Component class for the `<progress>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress
    '''
    TAG_NAME: ClassVar[str] = "progress"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['max', 'value']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        max: MaxType | _ImplDefinedType = _ImplDefined,
        value: ValueType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._max: MaxType | _ImplDefinedType = max
        self._value: ValueType | _ImplDefinedType = value

    @property
    def max(self) -> MaxType | None:
        return _handle_impl_defined(self._max)

    @property
    def value(self) -> ValueType | None:
        return _handle_impl_defined(self._value)

        
class QComponent(Component):
    '''
    Component class for the `<q>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/q
    '''
    TAG_NAME: ClassVar[str] = "q"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['cite']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        cite: CiteType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._cite: CiteType | _ImplDefinedType = cite

    @property
    def cite(self) -> CiteType | None:
        return _handle_impl_defined(self._cite)

        
class RpComponent(Component):
    '''
    Component class for the `<rp>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/rp
    '''
    TAG_NAME: ClassVar[str] = "rp"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class RtComponent(Component):
    '''
    Component class for the `<rt>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/rt
    '''
    TAG_NAME: ClassVar[str] = "rt"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class RubyComponent(Component):
    '''
    Component class for the `<ruby>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ruby
    '''
    TAG_NAME: ClassVar[str] = "ruby"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SComponent(Component):
    '''
    Component class for the `<s>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/s
    '''
    TAG_NAME: ClassVar[str] = "s"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SampComponent(Component):
    '''
    Component class for the `<samp>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/samp
    '''
    TAG_NAME: ClassVar[str] = "samp"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class ScriptComponent(Component):
    '''
    Component class for the `<script>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script
    '''
    TAG_NAME: ClassVar[str] = "script"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['async_', 'crossorigin', 'defer', 'fetchpriority', 'integrity', 'nomodule', 'nonce', 'referrerpolicy', 'src', 'type']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        async_: Async_Type | _ImplDefinedType = _ImplDefined,
        crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
        defer: DeferType | _ImplDefinedType = _ImplDefined,
        fetchpriority: FetchpriorityType | _ImplDefinedType = _ImplDefined,
        integrity: IntegrityType | _ImplDefinedType = _ImplDefined,
        nomodule: NomoduleType | _ImplDefinedType = _ImplDefined,
        nonce: NonceType | _ImplDefinedType = _ImplDefined,
        referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        type: TypeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._async_: Async_Type | _ImplDefinedType = async_
        self._crossorigin: CrossoriginType | _ImplDefinedType = crossorigin
        self._defer: DeferType | _ImplDefinedType = defer
        self._fetchpriority: FetchpriorityType | _ImplDefinedType = fetchpriority
        self._integrity: IntegrityType | _ImplDefinedType = integrity
        self._nomodule: NomoduleType | _ImplDefinedType = nomodule
        self._nonce: NonceType | _ImplDefinedType = nonce
        self._referrerpolicy: ReferrerpolicyType | _ImplDefinedType = referrerpolicy
        self._src: SrcType | _ImplDefinedType = src
        self._type: TypeType | _ImplDefinedType = type

    @property
    def async_(self) -> Async_Type | None:
        return _handle_impl_defined(self._async_)

    @property
    def crossorigin(self) -> CrossoriginType | None:
        return _handle_impl_defined(self._crossorigin)

    @property
    def defer(self) -> DeferType | None:
        return _handle_impl_defined(self._defer)

    @property
    def fetchpriority(self) -> FetchpriorityType | None:
        return _handle_impl_defined(self._fetchpriority)

    @property
    def integrity(self) -> IntegrityType | None:
        return _handle_impl_defined(self._integrity)

    @property
    def nomodule(self) -> NomoduleType | None:
        return _handle_impl_defined(self._nomodule)

    @property
    def nonce(self) -> NonceType | None:
        return _handle_impl_defined(self._nonce)

    @property
    def referrerpolicy(self) -> ReferrerpolicyType | None:
        return _handle_impl_defined(self._referrerpolicy)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

        
class SearchComponent(Component):
    '''
    Component class for the `<search>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/search
    '''
    TAG_NAME: ClassVar[str] = "search"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SectionComponent(Component):
    '''
    Component class for the `<section>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section
    '''
    TAG_NAME: ClassVar[str] = "section"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SelectComponent(Component):
    '''
    Component class for the `<select>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select
    '''
    TAG_NAME: ClassVar[str] = "select"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['autocomplete', 'autofocus', 'disabled', 'form', 'multiple', 'name', 'required', 'size']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        autocomplete: AutocompleteType | _ImplDefinedType = _ImplDefined,
        autofocus: AutofocusType | _ImplDefinedType = _ImplDefined,
        disabled: DisabledType | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
        multiple: MultipleType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
        required: RequiredType | _ImplDefinedType = _ImplDefined,
        size: SizeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._autocomplete: AutocompleteType | _ImplDefinedType = autocomplete
        self._autofocus: AutofocusType | _ImplDefinedType = autofocus
        self._disabled: DisabledType | _ImplDefinedType = disabled
        self._form: FormType | _ImplDefinedType = form
        self._multiple: MultipleType | _ImplDefinedType = multiple
        self._name: NameType | _ImplDefinedType = name
        self._required: RequiredType | _ImplDefinedType = required
        self._size: SizeType | _ImplDefinedType = size

    @property
    def autocomplete(self) -> AutocompleteType | None:
        return _handle_impl_defined(self._autocomplete)

    @property
    def autofocus(self) -> AutofocusType | None:
        return _handle_impl_defined(self._autofocus)

    @property
    def disabled(self) -> DisabledType | None:
        return _handle_impl_defined(self._disabled)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

    @property
    def multiple(self) -> MultipleType | None:
        return _handle_impl_defined(self._multiple)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

    @property
    def required(self) -> RequiredType | None:
        return _handle_impl_defined(self._required)

    @property
    def size(self) -> SizeType | None:
        return _handle_impl_defined(self._size)

        
class SlotComponent(Component):
    '''
    Component class for the `<slot>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/slot
    '''
    TAG_NAME: ClassVar[str] = "slot"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['name']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        name: NameType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._name: NameType | _ImplDefinedType = name

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

        
class SmallComponent(Component):
    '''
    Component class for the `<small>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/small
    '''
    TAG_NAME: ClassVar[str] = "small"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SourceComponent(Component):
    '''
    Component class for the `<source>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source
    '''
    TAG_NAME: ClassVar[str] = "source"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['type', 'src', 'srcset', 'sizes', 'media', 'height', 'width']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        type: TypeType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        srcset: SrcsetType | _ImplDefinedType = _ImplDefined,
        sizes: SizesType | _ImplDefinedType = _ImplDefined,
        media: MediaType | _ImplDefinedType = _ImplDefined,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._type: TypeType | _ImplDefinedType = type
        self._src: SrcType | _ImplDefinedType = src
        self._srcset: SrcsetType | _ImplDefinedType = srcset
        self._sizes: SizesType | _ImplDefinedType = sizes
        self._media: MediaType | _ImplDefinedType = media
        self._height: HeightType | _ImplDefinedType = height
        self._width: WidthType | _ImplDefinedType = width

    @property
    def type(self) -> TypeType | None:
        return _handle_impl_defined(self._type)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def srcset(self) -> SrcsetType | None:
        return _handle_impl_defined(self._srcset)

    @property
    def sizes(self) -> SizesType | None:
        return _handle_impl_defined(self._sizes)

    @property
    def media(self) -> MediaType | None:
        return _handle_impl_defined(self._media)

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

        
class SpanComponent(Component):
    '''
    Component class for the `<span>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/span
    '''
    TAG_NAME: ClassVar[str] = "span"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class StrongComponent(Component):
    '''
    Component class for the `<strong>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/strong
    '''
    TAG_NAME: ClassVar[str] = "strong"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class StyleComponent(Component):
    '''
    Component class for the `<style>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style
    '''
    TAG_NAME: ClassVar[str] = "style"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['media', 'nonce', 'title']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        media: MediaType | _ImplDefinedType = _ImplDefined,
        nonce: NonceType | _ImplDefinedType = _ImplDefined,
        title: TitleType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._media: MediaType | _ImplDefinedType = media
        self._nonce: NonceType | _ImplDefinedType = nonce
        self._title: TitleType | _ImplDefinedType = title

    @property
    def media(self) -> MediaType | None:
        return _handle_impl_defined(self._media)

    @property
    def nonce(self) -> NonceType | None:
        return _handle_impl_defined(self._nonce)

    @property
    def title(self) -> TitleType | None:
        return _handle_impl_defined(self._title)

        
class SubComponent(Component):
    '''
    Component class for the `<sub>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sub
    '''
    TAG_NAME: ClassVar[str] = "sub"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SummaryComponent(Component):
    '''
    Component class for the `<summary>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/summary
    '''
    TAG_NAME: ClassVar[str] = "summary"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class SupComponent(Component):
    '''
    Component class for the `<sup>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sup
    '''
    TAG_NAME: ClassVar[str] = "sup"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TableComponent(Component):
    '''
    Component class for the `<table>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table
    '''
    TAG_NAME: ClassVar[str] = "table"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TbodyComponent(Component):
    '''
    Component class for the `<tbody>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tbody
    '''
    TAG_NAME: ClassVar[str] = "tbody"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TdComponent(Component):
    '''
    Component class for the `<td>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/td
    '''
    TAG_NAME: ClassVar[str] = "td"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['colspan', 'headers', 'rowspan']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        colspan: ColspanType | _ImplDefinedType = _ImplDefined,
        headers: HeadersType | _ImplDefinedType = _ImplDefined,
        rowspan: RowspanType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._colspan: ColspanType | _ImplDefinedType = colspan
        self._headers: HeadersType | _ImplDefinedType = headers
        self._rowspan: RowspanType | _ImplDefinedType = rowspan

    @property
    def colspan(self) -> ColspanType | None:
        return _handle_impl_defined(self._colspan)

    @property
    def headers(self) -> HeadersType | None:
        return _handle_impl_defined(self._headers)

    @property
    def rowspan(self) -> RowspanType | None:
        return _handle_impl_defined(self._rowspan)

        
class TemplateComponent(Component):
    '''
    Component class for the `<template>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template
    '''
    TAG_NAME: ClassVar[str] = "template"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TextareaComponent(Component):
    '''
    Component class for the `<textarea>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea
    '''
    TAG_NAME: ClassVar[str] = "textarea"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['autocapitalize', 'autocomplete', 'autofocus', 'cols', 'dirname', 'disabled', 'form', 'maxlength', 'minlength', 'name', 'placeholder', 'readonly', 'required', 'rows', 'spellcheck', 'wrap']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        autocapitalize: AutocapitalizeType | _ImplDefinedType = _ImplDefined,
        autocomplete: AutocompleteType | _ImplDefinedType = _ImplDefined,
        autofocus: AutofocusType | _ImplDefinedType = _ImplDefined,
        cols: ColsType | _ImplDefinedType = _ImplDefined,
        dirname: DirnameType | _ImplDefinedType = _ImplDefined,
        disabled: DisabledType | _ImplDefinedType = _ImplDefined,
        form: FormType | _ImplDefinedType = _ImplDefined,
        maxlength: MaxlengthType | _ImplDefinedType = _ImplDefined,
        minlength: MinlengthType | _ImplDefinedType = _ImplDefined,
        name: NameType | _ImplDefinedType = _ImplDefined,
        placeholder: PlaceholderType | _ImplDefinedType = _ImplDefined,
        readonly: ReadonlyType | _ImplDefinedType = _ImplDefined,
        required: RequiredType | _ImplDefinedType = _ImplDefined,
        rows: RowsType | _ImplDefinedType = _ImplDefined,
        spellcheck: SpellcheckType | _ImplDefinedType = _ImplDefined,
        wrap: WrapType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._autocapitalize: AutocapitalizeType | _ImplDefinedType = autocapitalize
        self._autocomplete: AutocompleteType | _ImplDefinedType = autocomplete
        self._autofocus: AutofocusType | _ImplDefinedType = autofocus
        self._cols: ColsType | _ImplDefinedType = cols
        self._dirname: DirnameType | _ImplDefinedType = dirname
        self._disabled: DisabledType | _ImplDefinedType = disabled
        self._form: FormType | _ImplDefinedType = form
        self._maxlength: MaxlengthType | _ImplDefinedType = maxlength
        self._minlength: MinlengthType | _ImplDefinedType = minlength
        self._name: NameType | _ImplDefinedType = name
        self._placeholder: PlaceholderType | _ImplDefinedType = placeholder
        self._readonly: ReadonlyType | _ImplDefinedType = readonly
        self._required: RequiredType | _ImplDefinedType = required
        self._rows: RowsType | _ImplDefinedType = rows
        self._spellcheck: SpellcheckType | _ImplDefinedType = spellcheck
        self._wrap: WrapType | _ImplDefinedType = wrap

    @property
    def autocapitalize(self) -> AutocapitalizeType | None:
        return _handle_impl_defined(self._autocapitalize)

    @property
    def autocomplete(self) -> AutocompleteType | None:
        return _handle_impl_defined(self._autocomplete)

    @property
    def autofocus(self) -> AutofocusType | None:
        return _handle_impl_defined(self._autofocus)

    @property
    def cols(self) -> ColsType | None:
        return _handle_impl_defined(self._cols)

    @property
    def dirname(self) -> DirnameType | None:
        return _handle_impl_defined(self._dirname)

    @property
    def disabled(self) -> DisabledType | None:
        return _handle_impl_defined(self._disabled)

    @property
    def form(self) -> FormType | None:
        return _handle_impl_defined(self._form)

    @property
    def maxlength(self) -> MaxlengthType | None:
        return _handle_impl_defined(self._maxlength)

    @property
    def minlength(self) -> MinlengthType | None:
        return _handle_impl_defined(self._minlength)

    @property
    def name(self) -> NameType | None:
        return _handle_impl_defined(self._name)

    @property
    def placeholder(self) -> PlaceholderType | None:
        return _handle_impl_defined(self._placeholder)

    @property
    def readonly(self) -> ReadonlyType | None:
        return _handle_impl_defined(self._readonly)

    @property
    def required(self) -> RequiredType | None:
        return _handle_impl_defined(self._required)

    @property
    def rows(self) -> RowsType | None:
        return _handle_impl_defined(self._rows)

    @property
    def spellcheck(self) -> SpellcheckType | None:
        return _handle_impl_defined(self._spellcheck)

    @property
    def wrap(self) -> WrapType | None:
        return _handle_impl_defined(self._wrap)

        
class TfootComponent(Component):
    '''
    Component class for the `<tfoot>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tfoot
    '''
    TAG_NAME: ClassVar[str] = "tfoot"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class ThComponent(Component):
    '''
    Component class for the `<th>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th
    '''
    TAG_NAME: ClassVar[str] = "th"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['abbr', 'colspan', 'headers', 'rowspan', 'scope']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        abbr: AbbrType | _ImplDefinedType = _ImplDefined,
        colspan: ColspanType | _ImplDefinedType = _ImplDefined,
        headers: HeadersType | _ImplDefinedType = _ImplDefined,
        rowspan: RowspanType | _ImplDefinedType = _ImplDefined,
        scope: ScopeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._abbr: AbbrType | _ImplDefinedType = abbr
        self._colspan: ColspanType | _ImplDefinedType = colspan
        self._headers: HeadersType | _ImplDefinedType = headers
        self._rowspan: RowspanType | _ImplDefinedType = rowspan
        self._scope: ScopeType | _ImplDefinedType = scope

    @property
    def abbr(self) -> AbbrType | None:
        return _handle_impl_defined(self._abbr)

    @property
    def colspan(self) -> ColspanType | None:
        return _handle_impl_defined(self._colspan)

    @property
    def headers(self) -> HeadersType | None:
        return _handle_impl_defined(self._headers)

    @property
    def rowspan(self) -> RowspanType | None:
        return _handle_impl_defined(self._rowspan)

    @property
    def scope(self) -> ScopeType | None:
        return _handle_impl_defined(self._scope)

        
class TheadComponent(Component):
    '''
    Component class for the `<thead>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/thead
    '''
    TAG_NAME: ClassVar[str] = "thead"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TimeComponent(Component):
    '''
    Component class for the `<time>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time
    '''
    TAG_NAME: ClassVar[str] = "time"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['datetime']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        datetime: DatetimeType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._datetime: DatetimeType | _ImplDefinedType = datetime

    @property
    def datetime(self) -> DatetimeType | None:
        return _handle_impl_defined(self._datetime)

        
class TitleComponent(Component):
    '''
    Component class for the `<title>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/title
    '''
    TAG_NAME: ClassVar[str] = "title"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TrComponent(Component):
    '''
    Component class for the `<tr>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tr
    '''
    TAG_NAME: ClassVar[str] = "tr"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class TrackComponent(Component):
    '''
    Component class for the `<track>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track
    '''
    TAG_NAME: ClassVar[str] = "track"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['default', 'kind', 'label', 'src', 'srclang']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        default: DefaultType | _ImplDefinedType = _ImplDefined,
        kind: KindType | _ImplDefinedType = _ImplDefined,
        label: LabelType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        srclang: SrclangType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._default: DefaultType | _ImplDefinedType = default
        self._kind: KindType | _ImplDefinedType = kind
        self._label: LabelType | _ImplDefinedType = label
        self._src: SrcType | _ImplDefinedType = src
        self._srclang: SrclangType | _ImplDefinedType = srclang

    @property
    def default(self) -> DefaultType | None:
        return _handle_impl_defined(self._default)

    @property
    def kind(self) -> KindType | None:
        return _handle_impl_defined(self._kind)

    @property
    def label(self) -> LabelType | None:
        return _handle_impl_defined(self._label)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def srclang(self) -> SrclangType | None:
        return _handle_impl_defined(self._srclang)

        
class UComponent(Component):
    '''
    Component class for the `<u>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/u
    '''
    TAG_NAME: ClassVar[str] = "u"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class UlComponent(Component):
    '''
    Component class for the `<ul>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ul
    '''
    TAG_NAME: ClassVar[str] = "ul"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class VarComponent(Component):
    '''
    Component class for the `<var>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/var
    '''
    TAG_NAME: ClassVar[str] = "var"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
class VideoComponent(Component):
    '''
    Component class for the `<video>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video
    '''
    TAG_NAME: ClassVar[str] = "video"
    ATTRIBUTE_LIST: ClassVar[list[str]] = ['autoplay', 'controls', 'crossorigin', 'disableremoteplayback', 'height', 'loop', 'muted', 'playsinline', 'poster', 'preload', 'src', 'width']

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        autoplay: AutoplayType | _ImplDefinedType = _ImplDefined,
        controls: ControlsType | _ImplDefinedType = _ImplDefined,
        crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
        disableremoteplayback: DisableremoteplaybackType | _ImplDefinedType = _ImplDefined,
        height: HeightType | _ImplDefinedType = _ImplDefined,
        loop: LoopType | _ImplDefinedType = _ImplDefined,
        muted: MutedType | _ImplDefinedType = _ImplDefined,
        playsinline: PlaysinlineType | _ImplDefinedType = _ImplDefined,
        poster: PosterType | _ImplDefinedType = _ImplDefined,
        preload: PreloadType | _ImplDefinedType = _ImplDefined,
        src: SrcType | _ImplDefinedType = _ImplDefined,
        width: WidthType | _ImplDefinedType = _ImplDefined,
    ) -> None:
        super().__init__(__content, attributes)
        self._autoplay: AutoplayType | _ImplDefinedType = autoplay
        self._controls: ControlsType | _ImplDefinedType = controls
        self._crossorigin: CrossoriginType | _ImplDefinedType = crossorigin
        self._disableremoteplayback: DisableremoteplaybackType | _ImplDefinedType = disableremoteplayback
        self._height: HeightType | _ImplDefinedType = height
        self._loop: LoopType | _ImplDefinedType = loop
        self._muted: MutedType | _ImplDefinedType = muted
        self._playsinline: PlaysinlineType | _ImplDefinedType = playsinline
        self._poster: PosterType | _ImplDefinedType = poster
        self._preload: PreloadType | _ImplDefinedType = preload
        self._src: SrcType | _ImplDefinedType = src
        self._width: WidthType | _ImplDefinedType = width

    @property
    def autoplay(self) -> AutoplayType | None:
        return _handle_impl_defined(self._autoplay)

    @property
    def controls(self) -> ControlsType | None:
        return _handle_impl_defined(self._controls)

    @property
    def crossorigin(self) -> CrossoriginType | None:
        return _handle_impl_defined(self._crossorigin)

    @property
    def disableremoteplayback(self) -> DisableremoteplaybackType | None:
        return _handle_impl_defined(self._disableremoteplayback)

    @property
    def height(self) -> HeightType | None:
        return _handle_impl_defined(self._height)

    @property
    def loop(self) -> LoopType | None:
        return _handle_impl_defined(self._loop)

    @property
    def muted(self) -> MutedType | None:
        return _handle_impl_defined(self._muted)

    @property
    def playsinline(self) -> PlaysinlineType | None:
        return _handle_impl_defined(self._playsinline)

    @property
    def poster(self) -> PosterType | None:
        return _handle_impl_defined(self._poster)

    @property
    def preload(self) -> PreloadType | None:
        return _handle_impl_defined(self._preload)

    @property
    def src(self) -> SrcType | None:
        return _handle_impl_defined(self._src)

    @property
    def width(self) -> WidthType | None:
        return _handle_impl_defined(self._width)

        
class WbrComponent(Component):
    '''
    Component class for the `<wbr>` element.
    MDN Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/wbr
    '''
    TAG_NAME: ClassVar[str] = "wbr"
    ATTRIBUTE_LIST: ClassVar[list[str]] = []

    def __init__(
        self,
        *__content: Content,
        attributes: GlobalAttributes,
        
    ) -> None:
        super().__init__(__content, attributes)
        


        
def a(
    *__content: Content,
    download: DownloadType | _ImplDefinedType = _ImplDefined,
    href: HrefType | _ImplDefinedType = _ImplDefined,
    hreflang: HreflangType | _ImplDefinedType = _ImplDefined,
    ping: PingType | _ImplDefinedType = _ImplDefined,
    referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
    rel: RelType | _ImplDefinedType = _ImplDefined,
    target: TargetType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> AComponent:
    '''Component for the <a> element.'''
    return AComponent(
        *__content,
        attributes=global_attributes,
        download=download,
        href=href,
        hreflang=hreflang,
        ping=ping,
        referrerpolicy=referrerpolicy,
        rel=rel,
        target=target,
        type=type,
    )
def abbr(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> AbbrComponent:
    '''Component for the <abbr> element.'''
    return AbbrComponent(
        *__content,
        attributes=global_attributes,
        
    )
def address(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> AddressComponent:
    '''Component for the <address> element.'''
    return AddressComponent(
        *__content,
        attributes=global_attributes,
        
    )
def area(
    *__content: Content,
    alt: AltType | _ImplDefinedType = _ImplDefined,
    coords: CoordsType | _ImplDefinedType = _ImplDefined,
    download: DownloadType | _ImplDefinedType = _ImplDefined,
    href: HrefType | _ImplDefinedType = _ImplDefined,
    ping: PingType | _ImplDefinedType = _ImplDefined,
    referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
    rel: RelType | _ImplDefinedType = _ImplDefined,
    shape: ShapeType | _ImplDefinedType = _ImplDefined,
    target: TargetType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> AreaComponent:
    '''Component for the <area> element.'''
    return AreaComponent(
        *__content,
        attributes=global_attributes,
        alt=alt,
        coords=coords,
        download=download,
        href=href,
        ping=ping,
        referrerpolicy=referrerpolicy,
        rel=rel,
        shape=shape,
        target=target,
    )
def article(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> ArticleComponent:
    '''Component for the <article> element.'''
    return ArticleComponent(
        *__content,
        attributes=global_attributes,
        
    )
def aside(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> AsideComponent:
    '''Component for the <aside> element.'''
    return AsideComponent(
        *__content,
        attributes=global_attributes,
        
    )
def audio(
    *__content: Content,
    autoplay: AutoplayType | _ImplDefinedType = _ImplDefined,
    controls: ControlsType | _ImplDefinedType = _ImplDefined,
    crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
    disableremoteplayback: DisableremoteplaybackType | _ImplDefinedType = _ImplDefined,
    loop: LoopType | _ImplDefinedType = _ImplDefined,
    muted: MutedType | _ImplDefinedType = _ImplDefined,
    preload: PreloadType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> AudioComponent:
    '''Component for the <audio> element.'''
    return AudioComponent(
        *__content,
        attributes=global_attributes,
        autoplay=autoplay,
        controls=controls,
        crossorigin=crossorigin,
        disableremoteplayback=disableremoteplayback,
        loop=loop,
        muted=muted,
        preload=preload,
        src=src,
    )
def b(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> BComponent:
    '''Component for the <b> element.'''
    return BComponent(
        *__content,
        attributes=global_attributes,
        
    )
def base(
    *__content: Content,
    href: HrefType | _ImplDefinedType = _ImplDefined,
    target: TargetType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> BaseComponent:
    '''Component for the <base> element.'''
    return BaseComponent(
        *__content,
        attributes=global_attributes,
        href=href,
        target=target,
    )
def bdi(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> BdiComponent:
    '''Component for the <bdi> element.'''
    return BdiComponent(
        *__content,
        attributes=global_attributes,
        
    )
def bdo(
    *__content: Content,
    dir: DirType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> BdoComponent:
    '''Component for the <bdo> element.'''
    return BdoComponent(
        *__content,
        attributes=global_attributes,
        dir=dir,
    )
def blockquote(
    *__content: Content,
    cite: CiteType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> BlockquoteComponent:
    '''Component for the <blockquote> element.'''
    return BlockquoteComponent(
        *__content,
        attributes=global_attributes,
        cite=cite,
    )
def body(
    *__content: Content,
    onafterprint: OnafterprintType | _ImplDefinedType = _ImplDefined,
    onbeforeprint: OnbeforeprintType | _ImplDefinedType = _ImplDefined,
    onbeforeunload: OnbeforeunloadType | _ImplDefinedType = _ImplDefined,
    onblur: OnblurType | _ImplDefinedType = _ImplDefined,
    onerror: OnerrorType | _ImplDefinedType = _ImplDefined,
    onfocus: OnfocusType | _ImplDefinedType = _ImplDefined,
    onhashchange: OnhashchangeType | _ImplDefinedType = _ImplDefined,
    onlanguagechange: OnlanguagechangeType | _ImplDefinedType = _ImplDefined,
    onload: OnloadType | _ImplDefinedType = _ImplDefined,
    onmessage: OnmessageType | _ImplDefinedType = _ImplDefined,
    onoffline: OnofflineType | _ImplDefinedType = _ImplDefined,
    ononline: OnonlineType | _ImplDefinedType = _ImplDefined,
    onpopstate: OnpopstateType | _ImplDefinedType = _ImplDefined,
    onredo: OnredoType | _ImplDefinedType = _ImplDefined,
    onresize: OnresizeType | _ImplDefinedType = _ImplDefined,
    onstorage: OnstorageType | _ImplDefinedType = _ImplDefined,
    onundo: OnundoType | _ImplDefinedType = _ImplDefined,
    onunload: OnunloadType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> BodyComponent:
    '''Component for the <body> element.'''
    return BodyComponent(
        *__content,
        attributes=global_attributes,
        onafterprint=onafterprint,
        onbeforeprint=onbeforeprint,
        onbeforeunload=onbeforeunload,
        onblur=onblur,
        onerror=onerror,
        onfocus=onfocus,
        onhashchange=onhashchange,
        onlanguagechange=onlanguagechange,
        onload=onload,
        onmessage=onmessage,
        onoffline=onoffline,
        ononline=ononline,
        onpopstate=onpopstate,
        onredo=onredo,
        onresize=onresize,
        onstorage=onstorage,
        onundo=onundo,
        onunload=onunload,
    )
def br(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> BrComponent:
    '''Component for the <br> element.'''
    return BrComponent(
        *__content,
        attributes=global_attributes,
        
    )
def button(
    *__content: Content,
    autofocus: AutofocusType | _ImplDefinedType = _ImplDefined,
    disabled: DisabledType | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    formaction: FormactionType | _ImplDefinedType = _ImplDefined,
    formenctype: FormenctypeType | _ImplDefinedType = _ImplDefined,
    formmethod: FormmethodType | _ImplDefinedType = _ImplDefined,
    formnovalidate: FormnovalidateType | _ImplDefinedType = _ImplDefined,
    formtarget: FormtargetType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    popovertarget: PopovertargetType | _ImplDefinedType = _ImplDefined,
    popovertargetaction: PopovertargetactionType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    value: ValueType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ButtonComponent:
    '''Component for the <button> element.'''
    return ButtonComponent(
        *__content,
        attributes=global_attributes,
        autofocus=autofocus,
        disabled=disabled,
        form=form,
        formaction=formaction,
        formenctype=formenctype,
        formmethod=formmethod,
        formnovalidate=formnovalidate,
        formtarget=formtarget,
        name=name,
        popovertarget=popovertarget,
        popovertargetaction=popovertargetaction,
        type=type,
        value=value,
    )
def canvas(
    *__content: Content,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> CanvasComponent:
    '''Component for the <canvas> element.'''
    return CanvasComponent(
        *__content,
        attributes=global_attributes,
        height=height,
        width=width,
    )
def caption(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> CaptionComponent:
    '''Component for the <caption> element.'''
    return CaptionComponent(
        *__content,
        attributes=global_attributes,
        
    )
def cite(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> CiteComponent:
    '''Component for the <cite> element.'''
    return CiteComponent(
        *__content,
        attributes=global_attributes,
        
    )
def code(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> CodeComponent:
    '''Component for the <code> element.'''
    return CodeComponent(
        *__content,
        attributes=global_attributes,
        
    )
def col(
    *__content: Content,
    span: SpanType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ColComponent:
    '''Component for the <col> element.'''
    return ColComponent(
        *__content,
        attributes=global_attributes,
        span=span,
    )
def colgroup(
    *__content: Content,
    span: SpanType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ColgroupComponent:
    '''Component for the <colgroup> element.'''
    return ColgroupComponent(
        *__content,
        attributes=global_attributes,
        span=span,
    )
def data(
    *__content: Content,
    value: ValueType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> DataComponent:
    '''Component for the <data> element.'''
    return DataComponent(
        *__content,
        attributes=global_attributes,
        value=value,
    )
def datalist(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> DatalistComponent:
    '''Component for the <datalist> element.'''
    return DatalistComponent(
        *__content,
        attributes=global_attributes,
        
    )
def dd(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> DdComponent:
    '''Component for the <dd> element.'''
    return DdComponent(
        *__content,
        attributes=global_attributes,
        
    )
def del_(
    *__content: Content,
    cite: CiteType | _ImplDefinedType = _ImplDefined,
    datetime: DatetimeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> Del_Component:
    '''Component for the <del_> element.'''
    return Del_Component(
        *__content,
        attributes=global_attributes,
        cite=cite,
        datetime=datetime,
    )
def details(
    *__content: Content,
    open: OpenType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> DetailsComponent:
    '''Component for the <details> element.'''
    return DetailsComponent(
        *__content,
        attributes=global_attributes,
        open=open,
    )
def dfn(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> DfnComponent:
    '''Component for the <dfn> element.'''
    return DfnComponent(
        *__content,
        attributes=global_attributes,
        
    )
def dialog(
    *__content: Content,
    open: OpenType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> DialogComponent:
    '''Component for the <dialog> element.'''
    return DialogComponent(
        *__content,
        attributes=global_attributes,
        open=open,
    )
def div(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> DivComponent:
    '''Component for the <div> element.'''
    return DivComponent(
        *__content,
        attributes=global_attributes,
        
    )
def dl(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> DlComponent:
    '''Component for the <dl> element.'''
    return DlComponent(
        *__content,
        attributes=global_attributes,
        
    )
def dt(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> DtComponent:
    '''Component for the <dt> element.'''
    return DtComponent(
        *__content,
        attributes=global_attributes,
        
    )
def em(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> EmComponent:
    '''Component for the <em> element.'''
    return EmComponent(
        *__content,
        attributes=global_attributes,
        
    )
def embed(
    *__content: Content,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> EmbedComponent:
    '''Component for the <embed> element.'''
    return EmbedComponent(
        *__content,
        attributes=global_attributes,
        height=height,
        src=src,
        type=type,
        width=width,
    )
def fieldset(
    *__content: Content,
    disabled: DisabledType | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> FieldsetComponent:
    '''Component for the <fieldset> element.'''
    return FieldsetComponent(
        *__content,
        attributes=global_attributes,
        disabled=disabled,
        form=form,
        name=name,
    )
def figcaption(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> FigcaptionComponent:
    '''Component for the <figcaption> element.'''
    return FigcaptionComponent(
        *__content,
        attributes=global_attributes,
        
    )
def figure(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> FigureComponent:
    '''Component for the <figure> element.'''
    return FigureComponent(
        *__content,
        attributes=global_attributes,
        
    )
def footer(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> FooterComponent:
    '''Component for the <footer> element.'''
    return FooterComponent(
        *__content,
        attributes=global_attributes,
        
    )
def form(
    *__content: Content,
    accept_charset: Accept_charsetType | _ImplDefinedType = _ImplDefined,
    autocapitalize: AutocapitalizeType | _ImplDefinedType = _ImplDefined,
    autocomplete: AutocompleteType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    rel: RelType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> FormComponent:
    '''Component for the <form> element.'''
    return FormComponent(
        *__content,
        attributes=global_attributes,
        accept_charset=accept_charset,
        autocapitalize=autocapitalize,
        autocomplete=autocomplete,
        name=name,
        rel=rel,
    )
def h1(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> H1Component:
    '''Component for the <h1> element.'''
    return H1Component(
        *__content,
        attributes=global_attributes,
        
    )
def head(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> HeadComponent:
    '''Component for the <head> element.'''
    return HeadComponent(
        *__content,
        attributes=global_attributes,
        
    )
def header(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> HeaderComponent:
    '''Component for the <header> element.'''
    return HeaderComponent(
        *__content,
        attributes=global_attributes,
        
    )
def hgroup(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> HgroupComponent:
    '''Component for the <hgroup> element.'''
    return HgroupComponent(
        *__content,
        attributes=global_attributes,
        
    )
def hr(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> HrComponent:
    '''Component for the <hr> element.'''
    return HrComponent(
        *__content,
        attributes=global_attributes,
        
    )
def html(
    *__content: Content,
    xmlns: XmlnsType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> HtmlComponent:
    '''Component for the <html> element.'''
    return HtmlComponent(
        *__content,
        attributes=global_attributes,
        xmlns=xmlns,
    )
def i(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> IComponent:
    '''Component for the <i> element.'''
    return IComponent(
        *__content,
        attributes=global_attributes,
        
    )
def iframe(
    *__content: Content,
    allow: AllowType | _ImplDefinedType = _ImplDefined,
    allowfullscreen: AllowfullscreenType | _ImplDefinedType = _ImplDefined,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    loading: LoadingType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
    sandbox: SandboxType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    srcdoc: SrcdocType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> IframeComponent:
    '''Component for the <iframe> element.'''
    return IframeComponent(
        *__content,
        attributes=global_attributes,
        allow=allow,
        allowfullscreen=allowfullscreen,
        height=height,
        loading=loading,
        name=name,
        referrerpolicy=referrerpolicy,
        sandbox=sandbox,
        src=src,
        srcdoc=srcdoc,
        width=width,
    )
def img(
    *__content: Content,
    alt: AltType | _ImplDefinedType = _ImplDefined,
    crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
    decoding: DecodingType | _ImplDefinedType = _ImplDefined,
    elementtiming: ElementtimingType | _ImplDefinedType = _ImplDefined,
    fetchpriority: FetchpriorityType | _ImplDefinedType = _ImplDefined,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    ismap: IsmapType | _ImplDefinedType = _ImplDefined,
    loading: LoadingType | _ImplDefinedType = _ImplDefined,
    referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
    sizes: SizesType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    srcset: SrcsetType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    usemap: UsemapType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ImgComponent:
    '''Component for the <img> element.'''
    return ImgComponent(
        *__content,
        attributes=global_attributes,
        alt=alt,
        crossorigin=crossorigin,
        decoding=decoding,
        elementtiming=elementtiming,
        fetchpriority=fetchpriority,
        height=height,
        ismap=ismap,
        loading=loading,
        referrerpolicy=referrerpolicy,
        sizes=sizes,
        src=src,
        srcset=srcset,
        width=width,
        usemap=usemap,
    )
def input(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> InputComponent:
    '''Component for the <input> element.'''
    return InputComponent(
        *__content,
        attributes=global_attributes,
        
    )
def ins(
    *__content: Content,
    cite: CiteType | _ImplDefinedType = _ImplDefined,
    datetime: DatetimeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> InsComponent:
    '''Component for the <ins> element.'''
    return InsComponent(
        *__content,
        attributes=global_attributes,
        cite=cite,
        datetime=datetime,
    )
def kbd(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> KbdComponent:
    '''Component for the <kbd> element.'''
    return KbdComponent(
        *__content,
        attributes=global_attributes,
        
    )
def label(
    *__content: Content,
    for_: For_Type | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> LabelComponent:
    '''Component for the <label> element.'''
    return LabelComponent(
        *__content,
        attributes=global_attributes,
        for_=for_,
    )
def legend(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> LegendComponent:
    '''Component for the <legend> element.'''
    return LegendComponent(
        *__content,
        attributes=global_attributes,
        
    )
def li(
    *__content: Content,
    value: ValueType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> LiComponent:
    '''Component for the <li> element.'''
    return LiComponent(
        *__content,
        attributes=global_attributes,
        value=value,
    )
def link(
    *__content: Content,
    as_: As_Type | _ImplDefinedType = _ImplDefined,
    crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
    fetchpriority: FetchpriorityType | _ImplDefinedType = _ImplDefined,
    href: HrefType | _ImplDefinedType = _ImplDefined,
    hreflang: HreflangType | _ImplDefinedType = _ImplDefined,
    imagesizes: ImagesizesType | _ImplDefinedType = _ImplDefined,
    imagesrcset: ImagesrcsetType | _ImplDefinedType = _ImplDefined,
    integrity: IntegrityType | _ImplDefinedType = _ImplDefined,
    media: MediaType | _ImplDefinedType = _ImplDefined,
    referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
    rel: RelType | _ImplDefinedType = _ImplDefined,
    sizes: SizesType | _ImplDefinedType = _ImplDefined,
    title: TitleType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> LinkComponent:
    '''Component for the <link> element.'''
    return LinkComponent(
        *__content,
        attributes=global_attributes,
        as_=as_,
        crossorigin=crossorigin,
        fetchpriority=fetchpriority,
        href=href,
        hreflang=hreflang,
        imagesizes=imagesizes,
        imagesrcset=imagesrcset,
        integrity=integrity,
        media=media,
        referrerpolicy=referrerpolicy,
        rel=rel,
        sizes=sizes,
        title=title,
        type=type,
    )
def main(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> MainComponent:
    '''Component for the <main> element.'''
    return MainComponent(
        *__content,
        attributes=global_attributes,
        
    )
def map(
    *__content: Content,
    name: NameType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> MapComponent:
    '''Component for the <map> element.'''
    return MapComponent(
        *__content,
        attributes=global_attributes,
        name=name,
    )
def mark(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> MarkComponent:
    '''Component for the <mark> element.'''
    return MarkComponent(
        *__content,
        attributes=global_attributes,
        
    )
def menu(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> MenuComponent:
    '''Component for the <menu> element.'''
    return MenuComponent(
        *__content,
        attributes=global_attributes,
        
    )
def meta(
    *__content: Content,
    charset: CharsetType | _ImplDefinedType = _ImplDefined,
    content: ContentType | _ImplDefinedType = _ImplDefined,
    http_equiv: Http_equivType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> MetaComponent:
    '''Component for the <meta> element.'''
    return MetaComponent(
        *__content,
        attributes=global_attributes,
        charset=charset,
        content=content,
        http_equiv=http_equiv,
        name=name,
    )
def meter(
    *__content: Content,
    value: ValueType | _ImplDefinedType = _ImplDefined,
    min: MinType | _ImplDefinedType = _ImplDefined,
    max: MaxType | _ImplDefinedType = _ImplDefined,
    low: LowType | _ImplDefinedType = _ImplDefined,
    high: HighType | _ImplDefinedType = _ImplDefined,
    optimum: OptimumType | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> MeterComponent:
    '''Component for the <meter> element.'''
    return MeterComponent(
        *__content,
        attributes=global_attributes,
        value=value,
        min=min,
        max=max,
        low=low,
        high=high,
        optimum=optimum,
        form=form,
    )
def nav(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> NavComponent:
    '''Component for the <nav> element.'''
    return NavComponent(
        *__content,
        attributes=global_attributes,
        
    )
def noscript(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> NoscriptComponent:
    '''Component for the <noscript> element.'''
    return NoscriptComponent(
        *__content,
        attributes=global_attributes,
        
    )
def object(
    *__content: Content,
    data: DataType | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    usemap: UsemapType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ObjectComponent:
    '''Component for the <object> element.'''
    return ObjectComponent(
        *__content,
        attributes=global_attributes,
        data=data,
        form=form,
        height=height,
        name=name,
        type=type,
        usemap=usemap,
        width=width,
    )
def ol(
    *__content: Content,
    reversed: ReversedType | _ImplDefinedType = _ImplDefined,
    start: StartType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> OlComponent:
    '''Component for the <ol> element.'''
    return OlComponent(
        *__content,
        attributes=global_attributes,
        reversed=reversed,
        start=start,
        type=type,
    )
def optgroup(
    *__content: Content,
    disabled: DisabledType | _ImplDefinedType = _ImplDefined,
    label: LabelType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> OptgroupComponent:
    '''Component for the <optgroup> element.'''
    return OptgroupComponent(
        *__content,
        attributes=global_attributes,
        disabled=disabled,
        label=label,
    )
def option(
    *__content: Content,
    disabled: DisabledType | _ImplDefinedType = _ImplDefined,
    label: LabelType | _ImplDefinedType = _ImplDefined,
    selected: SelectedType | _ImplDefinedType = _ImplDefined,
    value: ValueType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> OptionComponent:
    '''Component for the <option> element.'''
    return OptionComponent(
        *__content,
        attributes=global_attributes,
        disabled=disabled,
        label=label,
        selected=selected,
        value=value,
    )
def output(
    *__content: Content,
    for_: For_Type | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> OutputComponent:
    '''Component for the <output> element.'''
    return OutputComponent(
        *__content,
        attributes=global_attributes,
        for_=for_,
        form=form,
        name=name,
    )
def p(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> PComponent:
    '''Component for the <p> element.'''
    return PComponent(
        *__content,
        attributes=global_attributes,
        
    )
def picture(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> PictureComponent:
    '''Component for the <picture> element.'''
    return PictureComponent(
        *__content,
        attributes=global_attributes,
        
    )
def pre(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> PreComponent:
    '''Component for the <pre> element.'''
    return PreComponent(
        *__content,
        attributes=global_attributes,
        
    )
def progress(
    *__content: Content,
    max: MaxType | _ImplDefinedType = _ImplDefined,
    value: ValueType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ProgressComponent:
    '''Component for the <progress> element.'''
    return ProgressComponent(
        *__content,
        attributes=global_attributes,
        max=max,
        value=value,
    )
def q(
    *__content: Content,
    cite: CiteType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> QComponent:
    '''Component for the <q> element.'''
    return QComponent(
        *__content,
        attributes=global_attributes,
        cite=cite,
    )
def rp(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> RpComponent:
    '''Component for the <rp> element.'''
    return RpComponent(
        *__content,
        attributes=global_attributes,
        
    )
def rt(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> RtComponent:
    '''Component for the <rt> element.'''
    return RtComponent(
        *__content,
        attributes=global_attributes,
        
    )
def ruby(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> RubyComponent:
    '''Component for the <ruby> element.'''
    return RubyComponent(
        *__content,
        attributes=global_attributes,
        
    )
def s(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SComponent:
    '''Component for the <s> element.'''
    return SComponent(
        *__content,
        attributes=global_attributes,
        
    )
def samp(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SampComponent:
    '''Component for the <samp> element.'''
    return SampComponent(
        *__content,
        attributes=global_attributes,
        
    )
def script(
    *__content: Content,
    async_: Async_Type | _ImplDefinedType = _ImplDefined,
    crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
    defer: DeferType | _ImplDefinedType = _ImplDefined,
    fetchpriority: FetchpriorityType | _ImplDefinedType = _ImplDefined,
    integrity: IntegrityType | _ImplDefinedType = _ImplDefined,
    nomodule: NomoduleType | _ImplDefinedType = _ImplDefined,
    nonce: NonceType | _ImplDefinedType = _ImplDefined,
    referrerpolicy: ReferrerpolicyType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ScriptComponent:
    '''Component for the <script> element.'''
    return ScriptComponent(
        *__content,
        attributes=global_attributes,
        async_=async_,
        crossorigin=crossorigin,
        defer=defer,
        fetchpriority=fetchpriority,
        integrity=integrity,
        nomodule=nomodule,
        nonce=nonce,
        referrerpolicy=referrerpolicy,
        src=src,
        type=type,
    )
def search(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SearchComponent:
    '''Component for the <search> element.'''
    return SearchComponent(
        *__content,
        attributes=global_attributes,
        
    )
def section(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SectionComponent:
    '''Component for the <section> element.'''
    return SectionComponent(
        *__content,
        attributes=global_attributes,
        
    )
def select(
    *__content: Content,
    autocomplete: AutocompleteType | _ImplDefinedType = _ImplDefined,
    autofocus: AutofocusType | _ImplDefinedType = _ImplDefined,
    disabled: DisabledType | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    multiple: MultipleType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    required: RequiredType | _ImplDefinedType = _ImplDefined,
    size: SizeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> SelectComponent:
    '''Component for the <select> element.'''
    return SelectComponent(
        *__content,
        attributes=global_attributes,
        autocomplete=autocomplete,
        autofocus=autofocus,
        disabled=disabled,
        form=form,
        multiple=multiple,
        name=name,
        required=required,
        size=size,
    )
def slot(
    *__content: Content,
    name: NameType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> SlotComponent:
    '''Component for the <slot> element.'''
    return SlotComponent(
        *__content,
        attributes=global_attributes,
        name=name,
    )
def small(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SmallComponent:
    '''Component for the <small> element.'''
    return SmallComponent(
        *__content,
        attributes=global_attributes,
        
    )
def source(
    *__content: Content,
    type: TypeType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    srcset: SrcsetType | _ImplDefinedType = _ImplDefined,
    sizes: SizesType | _ImplDefinedType = _ImplDefined,
    media: MediaType | _ImplDefinedType = _ImplDefined,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> SourceComponent:
    '''Component for the <source> element.'''
    return SourceComponent(
        *__content,
        attributes=global_attributes,
        type=type,
        src=src,
        srcset=srcset,
        sizes=sizes,
        media=media,
        height=height,
        width=width,
    )
def span(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SpanComponent:
    '''Component for the <span> element.'''
    return SpanComponent(
        *__content,
        attributes=global_attributes,
        
    )
def strong(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> StrongComponent:
    '''Component for the <strong> element.'''
    return StrongComponent(
        *__content,
        attributes=global_attributes,
        
    )
def style(
    *__content: Content,
    media: MediaType | _ImplDefinedType = _ImplDefined,
    nonce: NonceType | _ImplDefinedType = _ImplDefined,
    title: TitleType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> StyleComponent:
    '''Component for the <style> element.'''
    return StyleComponent(
        *__content,
        attributes=global_attributes,
        media=media,
        nonce=nonce,
        title=title,
    )
def sub(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SubComponent:
    '''Component for the <sub> element.'''
    return SubComponent(
        *__content,
        attributes=global_attributes,
        
    )
def summary(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SummaryComponent:
    '''Component for the <summary> element.'''
    return SummaryComponent(
        *__content,
        attributes=global_attributes,
        
    )
def sup(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> SupComponent:
    '''Component for the <sup> element.'''
    return SupComponent(
        *__content,
        attributes=global_attributes,
        
    )
def table(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TableComponent:
    '''Component for the <table> element.'''
    return TableComponent(
        *__content,
        attributes=global_attributes,
        
    )
def tbody(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TbodyComponent:
    '''Component for the <tbody> element.'''
    return TbodyComponent(
        *__content,
        attributes=global_attributes,
        
    )
def td(
    *__content: Content,
    colspan: ColspanType | _ImplDefinedType = _ImplDefined,
    headers: HeadersType | _ImplDefinedType = _ImplDefined,
    rowspan: RowspanType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> TdComponent:
    '''Component for the <td> element.'''
    return TdComponent(
        *__content,
        attributes=global_attributes,
        colspan=colspan,
        headers=headers,
        rowspan=rowspan,
    )
def template(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TemplateComponent:
    '''Component for the <template> element.'''
    return TemplateComponent(
        *__content,
        attributes=global_attributes,
        
    )
def textarea(
    *__content: Content,
    autocapitalize: AutocapitalizeType | _ImplDefinedType = _ImplDefined,
    autocomplete: AutocompleteType | _ImplDefinedType = _ImplDefined,
    autofocus: AutofocusType | _ImplDefinedType = _ImplDefined,
    cols: ColsType | _ImplDefinedType = _ImplDefined,
    dirname: DirnameType | _ImplDefinedType = _ImplDefined,
    disabled: DisabledType | _ImplDefinedType = _ImplDefined,
    form: FormType | _ImplDefinedType = _ImplDefined,
    maxlength: MaxlengthType | _ImplDefinedType = _ImplDefined,
    minlength: MinlengthType | _ImplDefinedType = _ImplDefined,
    name: NameType | _ImplDefinedType = _ImplDefined,
    placeholder: PlaceholderType | _ImplDefinedType = _ImplDefined,
    readonly: ReadonlyType | _ImplDefinedType = _ImplDefined,
    required: RequiredType | _ImplDefinedType = _ImplDefined,
    rows: RowsType | _ImplDefinedType = _ImplDefined,
    spellcheck: SpellcheckType | _ImplDefinedType = _ImplDefined,
    wrap: WrapType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> TextareaComponent:
    '''Component for the <textarea> element.'''
    return TextareaComponent(
        *__content,
        attributes=global_attributes,
        autocapitalize=autocapitalize,
        autocomplete=autocomplete,
        autofocus=autofocus,
        cols=cols,
        dirname=dirname,
        disabled=disabled,
        form=form,
        maxlength=maxlength,
        minlength=minlength,
        name=name,
        placeholder=placeholder,
        readonly=readonly,
        required=required,
        rows=rows,
        spellcheck=spellcheck,
        wrap=wrap,
    )
def tfoot(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TfootComponent:
    '''Component for the <tfoot> element.'''
    return TfootComponent(
        *__content,
        attributes=global_attributes,
        
    )
def th(
    *__content: Content,
    abbr: AbbrType | _ImplDefinedType = _ImplDefined,
    colspan: ColspanType | _ImplDefinedType = _ImplDefined,
    headers: HeadersType | _ImplDefinedType = _ImplDefined,
    rowspan: RowspanType | _ImplDefinedType = _ImplDefined,
    scope: ScopeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> ThComponent:
    '''Component for the <th> element.'''
    return ThComponent(
        *__content,
        attributes=global_attributes,
        abbr=abbr,
        colspan=colspan,
        headers=headers,
        rowspan=rowspan,
        scope=scope,
    )
def thead(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TheadComponent:
    '''Component for the <thead> element.'''
    return TheadComponent(
        *__content,
        attributes=global_attributes,
        
    )
def time(
    *__content: Content,
    datetime: DatetimeType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> TimeComponent:
    '''Component for the <time> element.'''
    return TimeComponent(
        *__content,
        attributes=global_attributes,
        datetime=datetime,
    )
def title(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TitleComponent:
    '''Component for the <title> element.'''
    return TitleComponent(
        *__content,
        attributes=global_attributes,
        
    )
def tr(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> TrComponent:
    '''Component for the <tr> element.'''
    return TrComponent(
        *__content,
        attributes=global_attributes,
        
    )
def track(
    *__content: Content,
    default: DefaultType | _ImplDefinedType = _ImplDefined,
    kind: KindType | _ImplDefinedType = _ImplDefined,
    label: LabelType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    srclang: SrclangType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> TrackComponent:
    '''Component for the <track> element.'''
    return TrackComponent(
        *__content,
        attributes=global_attributes,
        default=default,
        kind=kind,
        label=label,
        src=src,
        srclang=srclang,
    )
def u(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> UComponent:
    '''Component for the <u> element.'''
    return UComponent(
        *__content,
        attributes=global_attributes,
        
    )
def ul(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> UlComponent:
    '''Component for the <ul> element.'''
    return UlComponent(
        *__content,
        attributes=global_attributes,
        
    )
def var(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> VarComponent:
    '''Component for the <var> element.'''
    return VarComponent(
        *__content,
        attributes=global_attributes,
        
    )
def video(
    *__content: Content,
    autoplay: AutoplayType | _ImplDefinedType = _ImplDefined,
    controls: ControlsType | _ImplDefinedType = _ImplDefined,
    crossorigin: CrossoriginType | _ImplDefinedType = _ImplDefined,
    disableremoteplayback: DisableremoteplaybackType | _ImplDefinedType = _ImplDefined,
    height: HeightType | _ImplDefinedType = _ImplDefined,
    loop: LoopType | _ImplDefinedType = _ImplDefined,
    muted: MutedType | _ImplDefinedType = _ImplDefined,
    playsinline: PlaysinlineType | _ImplDefinedType = _ImplDefined,
    poster: PosterType | _ImplDefinedType = _ImplDefined,
    preload: PreloadType | _ImplDefinedType = _ImplDefined,
    src: SrcType | _ImplDefinedType = _ImplDefined,
    width: WidthType | _ImplDefinedType = _ImplDefined,
    **global_attributes: Unpack[GlobalAttributes],
) -> VideoComponent:
    '''Component for the <video> element.'''
    return VideoComponent(
        *__content,
        attributes=global_attributes,
        autoplay=autoplay,
        controls=controls,
        crossorigin=crossorigin,
        disableremoteplayback=disableremoteplayback,
        height=height,
        loop=loop,
        muted=muted,
        playsinline=playsinline,
        poster=poster,
        preload=preload,
        src=src,
        width=width,
    )
def wbr(
    *__content: Content,
    
    **global_attributes: Unpack[GlobalAttributes],
) -> WbrComponent:
    '''Component for the <wbr> element.'''
    return WbrComponent(
        *__content,
        attributes=global_attributes,
        
    )
__all__ = ('a','abbr','address','area','article','aside','audio','b','base','bdi','bdo','blockquote','body','br','button','canvas','caption','cite','code','col','colgroup','data','datalist','dd','del_','details','dfn','dialog','div','dl','dt','em','embed','fieldset','figcaption','figure','footer','form','h1','head','header','hgroup','hr','html','i','iframe','img','input','ins','kbd','label','legend','li','link','main','map','mark','menu','meta','meter','nav','noscript','object','ol','optgroup','option','output','p','picture','pre','progress','q','rp','rt','ruby','s','samp','script','search','section','select','slot','small','source','span','strong','style','sub','summary','sup','table','tbody','td','template','textarea','tfoot','th','thead','time','title','tr','track','u','ul','var','video','wbr')
