# คอมโพเนนต์และพร็อพ

จนถึงตอนนี้ เราสร้างแอปพลิเคชันทั้งหมดของเราในคอมโพเนนต์เดียว ซึ่ง
ก็เพียงพอสำหรับตัวอย่างเล็กๆ น้อยๆ แต่ในแอปพลิเคชันจริงใดๆ คุณจะต้อง
แยกส่วนติดต่อผู้ใช้ออกเป็นหลายคอมโพเนนต์ เพื่อให้คุณสามารถแบ่งส่วนติดต่อผู้ใช้
ออกเป็นชิ้นส่วนเล็กๆ ที่นำกลับมาใช้ซ้ำได้และประกอบกันได้

ลองใช้ตัวอย่างแถบความคืบหน้าของเรากัน สมมติว่าคุณต้องการแถบความคืบหน้าสองแถบ
แทนที่จะเป็นแถบเดียว: แถบหนึ่งเพิ่มขึ้นหนึ่งขีดต่อการคลิกหนึ่งครั้ง อีกแถบเพิ่มขึ้นสองขีด
ต่อการคลิกหนึ่งครั้ง

คุณ_ก็สามารถ_ทำได้โดยสร้างเอลิเมนต์ `<progress>` สองตัว:

```rust
let (count, set_count) = signal(0);
let double_count = move || count.get() * 2;

view! {
    <progress
        max="50"
        value=count
    />
    <progress
        max="50"
        value=double_count
    />
}
```

แต่แน่นอนว่า วิธีนี้ไม่ค่อยขยายขนาดได้ดีนัก หากคุณต้องการเพิ่มแถบ
ความคืบหน้าแถบที่สาม คุณต้องเพิ่มโค้ดนี้อีกครั้ง และหากคุณต้องการแก้ไขอะไรก็ตาม
เกี่ยวกับมัน คุณต้องแก้ไขถึงสามชุด

แต่เรามาสร้างคอมโพเนนต์ `<ProgressBar/>` กันดีกว่า

```rust
#[component]
fn ProgressBar() -> impl IntoView {
    view! {
        <progress
            max="50"
            // hmm... where will we get this from?
            value=progress
        />
    }
}
```

มีปัญหาอยู่อย่างหนึ่ง: `progress` ยังไม่ได้ถูกนิยาม มันควรมาจากไหน?
เมื่อก่อนที่เรานิยามทุกอย่างด้วยมือ เราก็แค่ใช้ชื่อตัวแปรโลคอล
ตอนนี้เราต้องมีวิธีส่งอาร์กิวเมนต์เข้าไปในคอมโพเนนต์

## พร็อพของคอมโพเนนต์

เราทำเช่นนี้โดยใช้พร็อพเพอร์ตีของคอมโพเนนต์ หรือ “พร็อพ (props)” หากคุณเคยใช้
ฟรอนต์เอนด์เฟรมเวิร์กอื่นมาก่อน แนวคิดนี้น่าจะคุ้นเคยดี โดยพื้นฐานแล้ว พร็อพเพอร์ตีของคอมโพเนนต์
ก็เปรียบเสมือนแอตทริบิวต์ของเอลิเมนต์ HTML: พวกมันช่วยให้คุณส่งข้อมูลเพิ่มเติม
เข้าไปในคอมโพเนนต์

ใน Leptos คุณนิยามพร็อพโดยการเพิ่มอาร์กิวเมนต์ให้กับฟังก์ชันคอมโพเนนต์

```rust
#[component]
fn ProgressBar(
    progress: ReadSignal<i32>
) -> impl IntoView {
    view! {
        <progress
            max="50"
            // now this works
            value=progress
        />
    }
}
```

ตอนนี้เราสามารถใช้คอมโพเนนต์ของเราในวิวของคอมโพเนนต์ `<App/>` หลักได้แล้ว

```rust
#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);
    view! {
        <button on:click=move |_| *set_count.write() += 1>
            "Click me"
        </button>
        // now we use our component!
        <ProgressBar progress=count/>
    }
}
```

การใช้คอมโพเนนต์ในวิวดูคล้ายกับการใช้เอลิเมนต์ HTML มาก คุณจะ
สังเกตได้ว่าคุณแยกความแตกต่างระหว่างเอลิเมนต์กับคอมโพเนนต์ได้ง่าย
เพราะคอมโพเนนต์ใช้ชื่อแบบ `PascalCase` เสมอ คุณส่งพร็อพ `progress`
เข้าไปราวกับว่ามันเป็นแอตทริบิวต์ของเอลิเมนต์ HTML ง่ายมาก

### พร็อพแบบรีแอกทีฟและแบบคงที่

คุณจะสังเกตได้ว่าในตัวอย่างนี้ `progress` รับ `ReadSignal<i32>`
แบบรีแอกทีฟ ไม่ใช่ `i32` ธรรมดา นี่คือ**สิ่งที่สำคัญมาก**

พร็อพของคอมโพเนนต์ไม่มีความหมายพิเศษใดๆ ติดอยู่ คอมโพเนนต์ก็เป็นเพียง
ฟังก์ชันที่รันครั้งเดียวเพื่อตั้งค่าส่วนติดต่อผู้ใช้ วิธีเดียวที่จะบอกให้
ส่วนติดต่อผู้ใช้ตอบสนองต่อการเปลี่ยนแปลงคือการส่งชนิดสัญญาณให้มัน ดังนั้นหากคุณมี
พร็อพเพอร์ตีของคอมโพเนนต์ที่จะเปลี่ยนแปลงไปตามกาลเวลา อย่าง `progress` ของเรา
มันก็ควรเป็นสัญญาณ

### พร็อพแบบ `optional`

ตอนนี้ค่าตั้ง `max` ถูกฮาร์ดโค้ดไว้ เรามาทำให้มันเป็นพร็อพด้วยกัน แต่
มาทำให้พร็อพนี้เป็นแบบไม่บังคับกัน เราทำได้โดยใส่แอนโนเทชัน `#[prop(optional)]` ให้มัน

```rust
#[component]
fn ProgressBar(
    // mark this prop optional
    // you can specify it or not when you use <ProgressBar/>
    #[prop(optional)]
    max: u16,
    progress: ReadSignal<i32>
) -> impl IntoView {
    view! {
        <progress
            max=max
            value=progress
        />
    }
}
```

ตอนนี้ เราสามารถใช้ `<ProgressBar max=50 progress=count/>` หรือจะละเว้น `max`
เพื่อใช้ค่าเริ่มต้นก็ได้ (กล่าวคือ `<ProgressBar progress=count/>`) ค่าเริ่มต้น
ของพร็อพ `optional` คือค่า `Default::default()` ของมัน ซึ่งสำหรับ `u16` จะ
เป็น `0` ในกรณีของแถบความคืบหน้า ค่า max เป็น `0` นั้นไม่มีประโยชน์เท่าไร

ดังนั้นเรามากำหนดค่าเริ่มต้นที่เจาะจงให้มันแทนดีกว่า

### พร็อพแบบ `default`

คุณสามารถระบุค่าเริ่มต้นอื่นที่ไม่ใช่ `Default::default()` ได้ง่ายๆ
ด้วย `#[prop(default = ...)`

```rust
#[component]
fn ProgressBar(
    #[prop(default = 100)]
    max: u16,
    progress: ReadSignal<i32>
) -> impl IntoView {
    view! {
        <progress
            max=max
            value=progress
        />
    }
}
```

### พร็อพแบบเจเนอริก

เยี่ยมมาก แต่เราเริ่มต้นด้วยตัวนับสองตัว ตัวหนึ่งขับเคลื่อนด้วย `count` และอีกตัว
ด้วยสัญญาณอนุพัทธ์ `double_count` เรามาสร้างสิ่งนั้นขึ้นมาใหม่โดยใช้ `double_count`
เป็นพร็อพ `progress` บน `<ProgressBar/>` อีกตัวหนึ่ง

```rust,compile_fail
#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);
    let double_count = move || count.get() * 2;

    view! {
        <button on:click=move |_| { set_count.update(|n| *n += 1); }>
            "Click me"
        </button>
        <ProgressBar progress=count/>
        // add a second progress bar
        <ProgressBar progress=double_count/>
    }
}
```

อืม... โค้ดนี้จะคอมไพล์ไม่ผ่าน น่าจะเข้าใจเหตุผลได้ไม่ยาก: เราได้ประกาศไว้ว่า
พร็อพ `progress` รับ `ReadSignal<i32>` และ `double_count` ไม่ใช่
`ReadSignal<i32>` ดังที่ rust-analyzer จะบอกคุณ ชนิดของมันคือ `|| -> i32` กล่าวคือ
มันเป็นโคลเชอร์ที่คืนค่า `i32`

มีสองสามวิธีในการจัดการเรื่องนี้ วิธีหนึ่งคือพูดว่า: “คือ ผมรู้ว่า
วิวจะเป็นรีแอกทีฟได้ มันต้องรับฟังก์ชันหรือสัญญาณ ผมสามารถแปลงสัญญาณ
ให้เป็นฟังก์ชันได้เสมอโดยห่อมันในโคลเชอร์... บางทีผมอาจ
รับฟังก์ชันอะไรก็ได้ไปเลย?”

หากคุณใช้ nightly Rust กับฟีเชอร์ `nightly` สัญญาณก็คือฟังก์ชัน
คุณจึงสามารถใช้คอมโพเนนต์แบบเจเนอริกและรับ `Fn() -> i32` ใดก็ได้:

```rust
#[component]
fn ProgressBar(
    #[prop(default = 100)]
    max: u16,
    progress: impl Fn() -> i32 + Send + Sync + 'static
) -> impl IntoView {
    view! {
        <progress
            max=max
            value=progress
        />
        // Add a line-break to avoid overlap
        <br/>
    }
}
```

> พร็อพแบบเจเนอริกสามารถระบุได้โดยใช้ `where` clause หรือใช้เจเนอริกแบบอินไลน์อย่าง `ProgressBar<F: Fn() -> i32 + 'static>` ก็ได้

คุณสามารถระบุเจเนอริกในวิวได้โดยใช้ไวยากรณ์สำหรับแสดงชนิดข้อมูล: `<Component<T>/>` (ไม่ใช่แบบสไตล์เทอร์โบฟิช `<Component::<T>/>`)

```rust
#[component]
fn SizeOf<T: Sized>(#[prop(marker)] _ty: PhantomData<T>) -> impl IntoView {
    std::mem::size_of::<T>()
}

#[component]
pub fn App() -> impl IntoView {
    view! {
        <SizeOf<usize>/>
        <SizeOf<String>/>
    }
}
```

> โปรดทราบว่ามีข้อจำกัดอยู่บ้าง ตัวอย่างเช่น พาร์เซอร์ของมาโคร view ของเราไม่สามารถจัดการเจเนอริกแบบซ้อนกันอย่าง `<SizeOf<Vec<T>>/>` ได้

### พร็อพแบบ `marker`

เจเนอริกจำเป็นต้องถูกใช้ที่ใดที่หนึ่งในพร็อพของคอมโพเนนต์ เพราะพร็อพถูกสร้างขึ้นเป็นสตรักต์ ดังนั้นชนิดเจเนอริกทั้งหมดจึงต้องถูกใช้ที่ใดที่หนึ่งในสตรักต์
เรื่องนี้ทำได้ง่ายๆ ด้วยพร็อพ `PhantomData` แบบไม่บังคับ: `#[prop(optional)] _ty: PhantomData<T>` แต่วิธีนี้จะสร้างเอกสารและเซ็ตเตอร์
สำหรับฟิลด์ `_ty` ขึ้นมา คุณสามารถใช้ `#[prop(marker)]` กับชนิดที่ถูกตั้งค่าเริ่มต้นเสมอได้ ซึ่งจะลบพร็อพออกจากเอกสารและบิลเดอร์
และจะใส่ `#[serde(skip)]` ให้ฟิลด์นั้นสำหรับ islands

### พร็อพแบบ `into`

หากคุณใช้ stable Rust สัญญาณไม่ได้อิมพลีเมนต์ `Fn()` โดยตรง เราสามารถห่อสัญญาณไว้ในโคลเชอร์ได้ (`move || progress.get()`)
แต่วิธีนั้นดูยุ่งเหยิงไปสักหน่อย

ยังมีวิธีอื่นที่เราสามารถทำได้ นั่นคือการใช้ `#[prop(into)]`
แอตทริบิวต์นี้จะเรียก `.into()` โดยอัตโนมัติกับค่าที่คุณส่งเป็นพร็อพ
ซึ่งช่วยให้คุณส่งพร็อพที่มีค่าต่างกันได้อย่างง่ายดาย

ในกรณีนี้ การรู้จัก
ชนิด [`Signal`](https://docs.rs/leptos/latest/leptos/reactive/wrappers/read/struct.Signal.html) ถือเป็นเรื่องที่มีประโยชน์ `Signal`
เป็นชนิดอีนัมที่แทนสัญญาณรีแอกทีฟแบบอ่านได้ทุกชนิด หรือค่าธรรมดา
มันมีประโยชน์เมื่อนิยาม API สำหรับคอมโพเนนต์ที่คุณต้องการนำกลับมาใช้ซ้ำ
พร้อมกับส่งสัญญาณชนิดต่างๆ กัน

```rust
#[component]
fn ProgressBar(
    #[prop(default = 100)]
    max: u16,
    #[prop(into)]
    progress: Signal<i32>
) -> impl IntoView
{
    view! {
        <progress
            max=max
            value=progress
        />
        <br/>
    }
}

#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);
    let double_count = move || count.get() * 2;

    view! {
        <button on:click=move |_| *set_count.write() += 1>
            "Click me"
        </button>
        // .into() converts `ReadSignal` to `Signal`
        <ProgressBar progress=count/>
        // use `Signal::derive()` to wrap a derived signal with the `Signal` type
        <ProgressBar progress=Signal::derive(double_count)/>
    }
}
```

### พร็อพแบบเจเนอริกที่ไม่บังคับ

โปรดทราบว่าคุณไม่สามารถระบุพร็อพแบบเจเนอริกที่ไม่บังคับให้คอมโพเนนต์ได้ เรามาดูกันว่าจะเกิดอะไรขึ้นหากคุณลอง:

```rust,compile_fail
#[component]
fn ProgressBar<F: Fn() -> i32 + Send + Sync + 'static>(
    #[prop(optional)] progress: Option<F>,
) -> impl IntoView {
    progress.map(|progress| {
        view! {
            <progress
                max=100
                value=progress
            />
            <br/>
        }
    })
}

#[component]
pub fn App() -> impl IntoView {
    view! {
        <ProgressBar/>
    }
}
```

Rust บอกข้อผิดพลาดอย่างเป็นประโยชน์ว่า

```
xx |         <ProgressBar/>
   |          ^^^^^^^^^^^ cannot infer type of the type parameter `F` declared on the function `ProgressBar`
   |
help: consider specifying the generic argument
   |
xx |         <ProgressBar::<F>/>
   |                     +++++
```

คุณสามารถระบุเจเนอริกบนคอมโพเนนต์ได้ด้วยไวยากรณ์ `<ProgressBar<F>/>` (ไม่ใช้เทอร์โบฟิชในมาโคร `view`) การระบุชนิดที่ถูกต้องตรงนี้เป็นไปไม่ได้ เพราะโคลเชอร์และฟังก์ชันโดยทั่วไปเป็นชนิดที่ไม่มีชื่อ คอมไพเลอร์สามารถแสดงพวกมันด้วยรูปแบบย่อได้ แต่คุณไม่สามารถระบุได้

อย่างไรก็ตาม คุณสามารถหลีกเลี่ยงปัญหานี้ได้โดยระบุชนิดที่เป็นรูปธรรมด้วย `Box<dyn _>` หรือ `&dyn _`:

```rust
#[component]
fn ProgressBar(
    #[prop(optional)] progress: Option<Box<dyn Fn() -> i32 + Send + Sync>>,
) -> impl IntoView {
    progress.map(|progress| {
        view! {
            <progress
                max=100
                value=progress
            />
            <br/>
        }
    })
}

#[component]
pub fn App() -> impl IntoView {
    view! {
        <ProgressBar/>
    }
}
```

เนื่องจากตอนนี้คอมไพเลอร์ Rust รู้ชนิดที่เป็นรูปธรรมของพร็อพ และด้วยเหตุนี้จึงรู้ขนาดในหน่วยความจำของมันแม้ในกรณี `None` โค้ดนี้จึงคอมไพล์ผ่านได้

> ในกรณีเฉพาะนี้ `&dyn Fn() -> i32` จะทำให้เกิดปัญหาไลฟ์ไทม์ แต่ในกรณีอื่นๆ มันอาจเป็นไปได้

## การเขียนเอกสารประกอบคอมโพเนนต์

นี่เป็นส่วนหนึ่งของหนังสือเล่มนี้ที่จำเป็นน้อยที่สุด แต่สำคัญที่สุด
การเขียนเอกสารประกอบคอมโพเนนต์และพร็อพของมันไม่ใช่สิ่งจำเป็นอย่างเคร่งครัด
แต่มันอาจสำคัญมาก ขึ้นอยู่กับขนาดทีมและแอปของคุณ แต่มันทำได้ง่ายมาก
และให้ผลตอบแทนทันที

การเขียนเอกสารให้คอมโพเนนต์และพร็อพของมัน คุณเพียงเพิ่มคอมเมนต์เอกสารบน
ฟังก์ชันคอมโพเนนต์ และบนพร็อพแต่ละตัว:

```rust
/// Shows progress toward a goal.
#[component]
fn ProgressBar(
    /// The maximum value of the progress bar.
    #[prop(default = 100)]
    max: u16,
    /// How much progress should be displayed.
    #[prop(into)]
    progress: Signal<i32>,
) -> impl IntoView {
    /* ... */
}
```

นั่นคือทั้งหมดที่คุณต้องทำ คอมเมนต์เหล่านี้ทำงานเหมือนคอมเมนต์เอกสาร Rust ทั่วไป
ยกเว้นว่าคุณสามารถเขียนเอกสารให้พร็อพของคอมโพเนนต์แต่ละตัวได้ ซึ่งทำไม่ได้
กับอาร์กิวเมนต์ของฟังก์ชัน Rust

สิ่งนี้จะสร้างเอกสารประกอบสำหรับคอมโพเนนต์ของคุณ ชนิด `Props` ของมัน
และฟิลด์แต่ละตัวที่ใช้เพิ่มพร็อพโดยอัตโนมัติ อาจเข้าใจได้ยากสักหน่อย
ว่าสิ่งนี้ทรงพลังเพียงใด จนกว่าคุณจะวางเมาส์เหนือชื่อคอมโพเนนต์หรือพร็อพ
และเห็นพลังของมาโคร `#[component]` ที่ผสานกับ rust-analyzer ตรงนี้

## การกระจายแอตทริบิวต์ไปยังคอมโพเนนต์

บางครั้งคุณต้องการให้ผู้ใช้สามารถเพิ่มแอตทริบิวต์เพิ่มเติมให้คอมโพเนนต์ได้ ตัวอย่างเช่น คุณอาจต้องการให้ผู้ใช้เพิ่มแอตทริบิวต์ `class` หรือ `id` ของตัวเองสำหรับการจัดสไตล์หรือวัตถุประสงค์อื่นๆ

คุณ_ก็สามารถ_ทำเช่นนี้ได้โดยสร้างพร็อพ `class` หรือ `id` แล้วนำไปใช้กับเอลิเมนต์ที่เหมาะสม แต่ Leptos ยังรองรับการ “กระจาย” แอตทริบิวต์เพิ่มเติมไปยังคอมโพเนนต์ด้วย แอตทริบิวต์ที่เพิ่มให้คอมโพเนนต์จะถูกนำไปใช้กับเอลิเมนต์ HTML ระดับบนสุดทั้งหมดที่คืนค่าจากวิวของมัน

```rust
// you can create attribute lists by using the view macro with a spread {..} as the tag name
let spread_onto_component = view! {
    <{..} aria-label="a component with attribute spreading"/>
};


view! {
    // attributes that are spread onto a component will be applied to *all* elements returned as part of
    // the component's view. to apply attributes to a subset of the component, pass them via a component prop
    <ComponentThatTakesSpread
        // plain identifiers are for props
        some_prop="foo"
        another_prop=42

        // the class:, style:, prop:, on: syntaxes work just as they do on elements
        class:foo=true
        style:font-weight="bold"
        prop:cool=42
        on:click=move |_| alert("clicked ComponentThatTakesSpread")

        // to pass a plain HTML attribute, prefix it with attr:
        attr:id="foo"

        // or, if you want to include multiple attributes, rather than prefixing each with
        // attr:, you can separate them from component props with the spread {..}
        {..} // everything after this is treated as an HTML attribute
        title="ooh, a title!"

        // we can add the whole list of attributes defined above
        {..spread_onto_component}
    />
}
```

``````admonish note
หากคุณต้องการแยกแอตทริบิวต์ออกมาเป็นฟังก์ชันเพื่อให้ใช้ได้ในหลายคอมโพเนนต์ คุณสามารถทำได้โดยอิมพลีเมนต์ฟังก์ชันที่คืนค่า `impl Attribute`

ตัวอย่างข้างต้นก็จะมีหน้าตาแบบนี้:

```rust
fn spread_onto_component() -> impl Attribute {
    view!{
        <{..} aria-label="a component with attribute spreading"/>
    }
}

view!{
    <SomeComponent {..spread_onto_component()} />
}
```
``````

หากคุณต้องการกระจายแอตทริบิวต์ไปยังคอมโพเนนต์ แต่ต้องการนำแอตทริบิวต์ไปใช้กับอย่างอื่นนอกเหนือจากเอลิเมนต์ระดับบนสุดทั้งหมด ให้ใช้ [`AttributeInterceptor`](https://docs.rs/leptos/latest/leptos/attribute_interceptor/fn.AttributeInterceptor.html)

ดู[ตัวอย่าง `spread`](https://github.com/leptos-rs/leptos/blob/main/examples/spread/src/lib.rs) สำหรับตัวอย่างเพิ่มเติม

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/3-components-0-7-rkjn3j?file=%2Fsrc%2Fmain.rs%3A39%2C10)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/3-components-0-7-rkjn3j?file=%2Fsrc%2Fmain.rs%3A39%2C10" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

// Composing different components together is how we build
// user interfaces. Here, we'll define a reusable <ProgressBar/>.
// You'll see how doc comments can be used to document components
// and their properties.

/// Shows progress toward a goal.
#[component]
fn ProgressBar(
    // Marks this as an optional prop. It will default to the default
    // value of its type, i.e., 0.
    #[prop(default = 100)]
    /// The maximum value of the progress bar.
    max: u16,
    // Will run `.into()` on the value passed into the prop.
    #[prop(into)]
    // `Signal<T>` is a wrapper for several reactive types.
    // It can be helpful in component APIs like this, where we
    // might want to take any kind of reactive value
    /// How much progress should be displayed.
    progress: Signal<i32>,
) -> impl IntoView {
    view! {
        <progress
            max={max}
            value=progress
        />
        <br/>
    }
}

#[component]
fn App() -> impl IntoView {
    let (count, set_count) = signal(0);

    let double_count = move || count.get() * 2;

    view! {
        <button
            on:click=move |_| {
                *set_count.write() += 1;
            }
        >
            "Click me"
        </button>
        <br/>
        // If you have this open in CodeSandbox or an editor with
        // rust-analyzer support, try hovering over `ProgressBar`,
        // `max`, or `progress` to see the docs we defined above
        <ProgressBar max=50 progress=count/>
        // Let's use the default max value on this one
        // the default is 100, so it should move half as fast
        <ProgressBar progress=count/>
        // Signal::derive creates a Signal wrapper from our derived signal
        // using double_count means it should move twice as fast
        <ProgressBar max=50 progress=Signal::derive(double_count)/>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
