# คอมโพเนนต์และพร็อพ

จนถึงตอนนี้ เราเขียนแอปพลิเคชันทั้งหมดรวมอยู่ในคอมโพเนนต์เดียว ซึ่งก็เพียงพอสำหรับตัวอย่างขนาดเล็ก แต่ในการพัฒนาแอปพลิเคชันจริง คุณย่อมต้องการแยก UI ออกเป็นหลายคอมโพเนนต์ เพื่อแบ่งหน้าตาและการทำงานออกเป็นชิ้นส่วนย่อย ๆ ที่นำกลับมาใช้ซ้ำและประกอบเข้าด้วยกันได้อย่างยืดหยุ่น

ลองนำตัวอย่างแถบความคืบหน้า (progress bar) มาดูกัน สมมติว่าคุณต้องการแถบความคืบหน้าสองแถบแทนที่จะมีแค่อันเดียว โดยแถบแรกจะเพิ่มขึ้นทีละ 1 ต่อการคลิกหนึ่งครั้ง ส่วนอีกแถบเพิ่มขึ้นทีละ 2

คุณ_อาจจะ_เขียนตรง ๆ ด้วยการใส่เอลิเมนต์ `<progress>` สองตัวแบบนี้:

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

แต่แน่นอนว่า วิธีนี้ปรับขยาย (scale) ได้ยาก หากต้องการเพิ่มแถบความคืบหน้าอันที่สาม คุณก็ต้องก๊อปปี้โค้ดนี้ซ้ำอีกรอบ และถ้าอยากปรับแต่งอะไร ก็ต้องตามไปแก้ให้ครบทั้งสามที่

ดังนั้น เรามาแยกสร้างเป็นคอมโพเนนต์ `<ProgressBar/>` กันดีกว่า:

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

ทว่ามีปัญหาอยู่จุดหนึ่ง นั่นคือ `progress` ยังไม่ได้ถูกประกาศ แล้วมันควรจะมาจากไหนกันล่ะ? ก่อนหน้านี้ที่เราเขียนทุกอย่างรวมกัน เราก็แค่อ้างอิงชื่อตัวแปรในขอบเขตเดียวกันได้เลย แต่คราวนี้เราจำเป็นต้องมีวิธีส่งอาร์กิวเมนต์เข้าไปยังคอมโพเนนต์

## พร็อพของคอมโพเนนต์

เราจัดการเรื่องนี้ได้ผ่านคุณสมบัติของคอมโพเนนต์ หรือที่เรียกสั้น ๆ ว่า “พร็อพ (props)” หากคุณเคยใช้ฟรอนต์เอนด์เฟรมเวิร์กอื่น ๆ มาก่อน ก็น่าจะคุ้นเคยกับแนวคิดนี้เป็นอย่างดี โดยพื้นฐานแล้ว พร็อพของคอมโพเนนต์ก็ทำงานคล้ายกับแอตทริบิวต์ของเอลิเมนต์ HTML นั่นคือเปิดทางให้เราส่งข้อมูลจากภายนอกเข้าไปในคอมโพเนนต์ได้

ใน Leptos คุณสามารถกำหนดพร็อพได้ง่าย ๆ เพียงเพิ่มพารามิเตอร์ให้กับฟังก์ชันคอมโพเนนต์:

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

ตอนนี้เราสามารถนำคอมโพเนนต์นี้ไปใช้งานในวิวของคอมโพเนนต์หลักอย่าง `<App/>` ได้แล้ว:

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

การเรียกใช้คอมโพเนนต์ในวิวจะเหมือนกับการใช้เอลิเมนต์ HTML ทั่วไป โดยคุณสามารถแยกความแตกต่างได้ง่าย ๆ เพราะคอมโพเนนต์จะใช้ชื่อแบบ `PascalCase` เสมอ และคุณก็ส่งพร็อพ `progress` เข้าไปราวกับเป็นแอตทริบิวต์ตัวหนึ่งของ HTML ได้อย่างตรงไปตรงมา

### พร็อพแบบรีแอกทีฟและแบบคงที่

คุณจะสังเกตเห็นว่าในตัวอย่างนี้ พร็อพ `progress` รับชนิดข้อมูลรีแอกทีฟอย่าง `ReadSignal<i32>` ไม่ใช่แค่ค่า `i32` ธรรมดา เรื่องนี้ถือเป็น**หัวใจสำคัญอย่างยิ่ง**

พร็อพของคอมโพเนนต์ไม่ได้มีเวทมนตร์หรือความหมายพิเศษอะไรซ่อนอยู่ คอมโพเนนต์เป็นเพียงฟังก์ชันธรรมดาที่ถูกรันแค่ครั้งเดียวเพื่อเซ็ตอัป UI เท่านั้น ดังนั้น วิธีเดียวที่จะสั่งให้ UI อัปเดตตามการเปลี่ยนแปลงได้ คือคุณต้องส่งชนิดข้อมูลแบบสัญญาณ (signal) เข้าไป และถ้าคอมโพเนนต์ของคุณมีพร็อพที่จะต้องเปลี่ยนแปลงค่าตามเวลาได้ เช่น `progress` ในตัวอย่างนี้ พร็อพนั้นก็จำเป็นต้องเป็นสัญญาณ

### พร็อพแบบ `optional`

ในตอนนี้ค่า `max` ยังถูกฮาร์ดโค้ดไว้อยู่ เรามาแปลงมันให้เป็นพร็อพกันดีกว่า และเพื่อให้ยืดหยุ่นขึ้น เราจะกำหนดให้พร็อพนี้เป็นแบบไม่บังคับ (optional) ผ่านการใส่แอตทริบิวต์ `#[prop(optional)]`:

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

คราวนี้ เราจะเรียกใช้ `<ProgressBar max=50 progress=count/>` หรือจะละเว้นไม่ส่ง `max` เพื่อใช้ค่าเริ่มต้นก็ได้ (เช่น `<ProgressBar progress=count/>`) โดยค่าเริ่มต้นของพร็อพ `optional` จะดึงมาจาก `Default::default()` ของชนิดข้อมูลนั้น ๆ ซึ่งสำหรับ `u16` ก็คือ `0` แต่ในกรณีของแถบความคืบหน้า การมีค่า max เป็น `0` คงไม่ค่อยมีประโยชน์เท่าไหร่

ดังนั้น เรามากำหนดค่าเริ่มต้นที่เหมาะสมให้กับมันแทนดีกว่า

### พร็อพแบบ `default`

คุณสามารถระบุค่าเริ่มต้นอื่น ๆ ที่ไม่ใช่ `Default::default()` ได้อย่างง่ายดายด้วย `#[prop(default = ...)]`:

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

ยอดเยี่ยม! แต่จำได้ไหมว่าตอนแรกเรามีแถบความคืบหน้าสองอัน อันหนึ่งผูกกับ `count` และอีกอันผูกกับสัญญาณอนุพัทธ์อย่าง `double_count` ลองนำ `double_count` มาส่งเป็นพร็อพ `progress` ให้กับ `<ProgressBar/>` อีกอันดู:

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

แน่นอนว่าโค้ดนี้จะคอมไพล์ไม่ผ่าน และสาเหตุก็เข้าใจได้ไม่ยาก: เราประกาศไว้ว่าพร็อพ `progress` รับค่า `ReadSignal<i32>` แต่ `double_count` ไม่ใช่ `ReadSignal<i32>` โดย rust-analyzer จะแจ้งว่าชนิดของมันคือ `|| -> i32` ซึ่งก็คือโคลเชอร์ที่คืนค่า `i32` นั่นเอง

เราสามารถแก้ปัญหานี้ได้หลายแบบ วิธีหนึ่งคือคิดว่า: “เรารู้อยู่แล้วว่าการที่วิวจะตอบสนองแบบรีแอกทีฟได้ มันต้องรับฟังก์ชันหรือสัญญาณ และเราก็แปลงสัญญาณให้กลายเป็นฟังก์ชันได้เสมอด้วยการห่อไว้ในโคลเชอร์... ถ้างั้นเราทำคอมโพเนนต์ให้รับฟังก์ชันอะไรก็ได้ไปเลยดีไหม?”

หากคุณใช้ nightly Rust ร่วมกับฟีเชอร์ `nightly` สัญญาณก็คือฟังก์ชันอยู่แล้ว คุณจึงสามารถใช้คอมโพเนนต์แบบเจเนอริกและรับค่า `Fn() -> i32` ใดก็ได้:

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

เวลาเรียกใช้ในวิว คุณสามารถระบุชนิดเจเนอริกได้โดยใช้ไวยากรณ์สำหรับแสดงชนิดข้อมูล: `<Component<T>/>` (ไม่ใช่สไตล์เทอร์โบฟิชอย่าง `<Component::<T>/>`)

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

> โปรดทราบว่ามีข้อจำกัดอยู่บ้าง ตัวอย่างเช่น พาร์เซอร์ของมาโคร view ยังไม่สามารถจัดการเจเนอริกแบบซ้อนกันอย่าง `<SizeOf<Vec<T>>/>` ได้

### พร็อพแบบ `marker`

พารามิเตอร์ชนิดเจเนอริกจำเป็นต้องถูกใช้งานที่ใดที่หนึ่งในพร็อพของคอมโพเนนต์ เพราะเบื้องหลังนั้นพร็อพจะถูกแปลงไปเป็นโครงสร้างสตรักต์ ทำให้ทุกชนิดข้อมูลเจเนอริกต้องปรากฏอยู่ในฟิลด์ใดฟิลด์หนึ่งตามกฎของ Rust
เรื่องนี้ทำได้ง่าย ๆ ด้วยการใช้พร็อพ `PhantomData` แบบไม่บังคับ: `#[prop(optional)] _ty: PhantomData<T>` แต่วิธีนี้จะสร้างเอกสารประกอบและเมธอดเซ็ตเตอร์สำหรับฟิลด์ `_ty` ขึ้นมาด้วย คุณจึงสามารถใช้ `#[prop(marker)]` กับชนิดที่ถูกตั้งค่าเริ่มต้นเสมอได้ ซึ่งจะตัดพร็อพนี้ออกจากเอกสารและบิลเดอร์ พร้อมทั้งใส่ `#[serde(skip)]` ให้กับฟิลด์นั้นสำหรับการทำงานร่วมกับ islands

### พร็อพแบบ `into`

หากคุณใช้งานบน stable Rust สัญญาณจะไม่ได้อิมพลีเมนต์ `Fn()` โดยตรง แม้เราจะห่อสัญญาณไว้ในโคลเชอร์ได้ (`move || progress.get()`) แต่วิธีนั้นก็ดูรุงรังไปสักหน่อย

เรายังมีอีกวิธีที่ทำได้ นั่นคือการใช้ `#[prop(into)]`
แอตทริบิวต์นี้จะเรียก `.into()` กับค่าที่คุณส่งเข้ามาในพร็อพให้โดยอัตโนมัติ ช่วยให้คุณส่งค่าหลากชนิดที่สามารถแปลงเข้ากันได้เข้ามาได้อย่างสะดวกง่ายดาย

ในกรณีนี้ การรู้จักชนิดข้อมูล [`Signal`](https://docs.rs/leptos/latest/leptos/reactive/wrappers/read/struct.Signal.html) จะมีประโยชน์อย่างยิ่ง เพราะ `Signal` เป็นชนิดอีนัมที่ห่อหุ้มสัญญาณรีแอกทีฟแบบอ่านได้ทุกชนิด หรือแม้กระทั่งค่าคงที่ธรรมดา มันจึงมีประโยชน์มากเมื่อต้องออกแบบ API สำหรับคอมโพเนนต์ที่คุณต้องการนำกลับมาใช้ซ้ำ ร่วมกับการส่งสัญญาณชนิดต่าง ๆ กัน

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

ข้อควรระวังคือ คุณไม่สามารถสร้างพร็อพที่เป็นทั้งเจเนอริกและเป็นแบบไม่บังคับ (optional) บนคอมโพเนนต์ได้โดยตรง ลองมาดูตัวอย่างว่าจะเกิดอะไรขึ้นหากคุณลองเขียนแบบนี้:

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

Rust จะแจ้งข้อผิดพลาดอย่างชัดเจนว่า:

```
xx |         <ProgressBar/>
   |          ^^^^^^^^^^^ cannot infer type of the type parameter `F` declared on the function `ProgressBar`
   |
help: consider specifying the generic argument
   |
xx |         <ProgressBar::<F>/>
   |                     +++++
```

แม้คุณจะสามารถระบุเจเนอริกบนคอมโพเนนต์ได้ด้วยไวยากรณ์ `<ProgressBar<F>/>` (ไม่ใช้เทอร์โบฟิชในมาโคร `view`) แต่การระบุชนิดที่ถูกต้องตรงนี้เป็นไปไม่ได้ในทางปฏิบัติ เพราะโคลเชอร์และฟังก์ชันโดยทั่วไปเป็นชนิดที่ไม่มีชื่อระบุได้ (unnamed types) คอมไพเลอร์เพียงแค่สร้างชนิดเฉพาะขึ้นมาภายใน แต่เราไม่สามารถพิมพ์ระบุชื่อชนิดนั้นลงไปตรง ๆ ได้

อย่างไรก็ตาม คุณสามารถหลีกเลี่ยงปัญหานี้ได้โดยระบุชนิดที่เป็นรูปธรรม (concrete type) ด้วย `Box<dyn _>` หรือ `&dyn _`:

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

เนื่องจากตอนนี้คอมไพเลอร์ Rust รู้ชนิดที่เป็นรูปธรรมของพร็อพแล้ว และด้วยเหตุนี้จึงรู้ขนาดในหน่วยความจำของมันแม้ในกรณี `None` โค้ดนี้จึงคอมไพล์ผ่านได้

> ในกรณีเฉพาะนี้ `&dyn Fn() -> i32` จะทำให้เกิดปัญหาเรื่องไลฟ์ไทม์ แต่ในกรณีอื่น ๆ ก็อาจนำมาปรับใช้ได้

## การเขียนเอกสารประกอบคอมโพเนนต์

นี่เป็นส่วนหนึ่งของหนังสือเล่มนี้ที่ดูเหมือนจำเป็นน้อยที่สุด แต่จริง ๆ แล้วทรงคุณค่าที่สุดหัวข้อหนึ่ง การเขียนเอกสารประกอบคอมโพเนนต์และพร็อพของมันอาจไม่ใช่ข้อบังคับทางเทคนิค แต่มันจะมีบทบาทสำคัญอย่างมากเมื่อโปรเจกต์และทีมของคุณเติบโตขึ้น อีกทั้งยังทำได้ง่ายมากใน Leptos และให้ผลตอบแทนทันตา

หากต้องการเขียนเอกสารกำกับคอมโพเนนต์และพร็อพของมัน คุณเพียงเพิ่มคอมเมนต์เอกสาร (doc comments ขึ้นต้นด้วย `///`) บนฟังก์ชันคอมโพเนนต์ และบนพร็อพแต่ละตัวได้เลย:

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

นั่นคือทั้งหมดที่คุณต้องทำ! คอมเมนต์เหล่านี้ทำงานเหมือนคอมเมนต์เอกสารทั่วไปของ Rust ทุกประการ ยกเว้นว่าคุณสามารถเขียนเอกสารกำกับพร็อพของคอมโพเนนต์แต่ละตัวแยกกันได้ ซึ่งปกติแล้วฟังก์ชันทั่วไปใน Rust ไม่สามารถทำได้ (ไม่สามารถเขียน doc comment เหนือพารามิเตอร์ของฟังก์ชันตรง ๆ)

สิ่งนี้จะนำไปสร้างเอกสารประกอบสำหรับคอมโพเนนต์ โครงสร้างสตรักต์ `Props` ของมัน และแต่ละฟิลด์ของพร็อพโดยอัตโนมัติ คุณอาจจะยังไม่เห็นภาพว่าสิ่งนี้ทรงพลังเพียงใด จนกว่าคุณจะได้ลองวางเมาส์เหนือชื่อคอมโพเนนต์หรือพร็อพ แล้วเห็นเอกสารคำอธิบายปรากฏขึ้นมาผ่านการทำงานร่วมกันของมาโคร `#[component]` และ rust-analyzer

## การกระจายแอตทริบิวต์ไปยังคอมโพเนนต์

ในบางครั้ง คุณอาจต้องการเปิดโอกาสให้ผู้ใช้งานสามารถเพิ่มแอตทริบิวต์เพิ่มเติมให้กับคอมโพเนนต์ได้ ตัวอย่างเช่น คุณอาจต้องการให้ผู้ใช้ใส่แอตทริบิวต์ `class` หรือ `id` ของตัวเองสำหรับการจัดสไตล์หรือวัตถุประสงค์อื่น ๆ

คุณ_อาจจะ_ทำเช่นนี้ได้โดยสร้างพร็อพ `class` หรือ `id` ขึ้นมารับค่าแล้วนำไปผูกกับเอลิเมนต์ที่ต้องการ แต่ Leptos ยังรองรับการ “กระจาย (spread)” แอตทริบิวต์เพิ่มเติมไปยังคอมโพเนนต์ได้โดยตรง โดยแอตทริบิวต์ที่ส่งไปยังคอมโพเนนต์จะถูกส่งต่อไปยังเอลิเมนต์ HTML ระดับบนสุด (top-level elements) ทั้งหมดที่คืนค่าออกมาจากวิวของคอมโพเนนต์นั้น

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
หากคุณต้องการแยกชุดแอตทริบิวต์ออกมาเป็นฟังก์ชันเพื่อนำไปใช้ซ้ำในหลาย ๆ คอมโพเนนต์ คุณสามารถทำได้โดยเขียนฟังก์ชันที่คืนค่าเป็น `impl Attribute`

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

หากคุณต้องการกระจายแอตทริบิวต์ไปยังคอมโพเนนต์ แต่ต้องการนำแอตทริบิวต์ไปใช้กับตำแหน่งอื่นนอกเหนือจากเอลิเมนต์ระดับบนสุดทั้งหมด คุณสามารถควบคุมได้ผ่าน [`AttributeInterceptor`](https://docs.rs/leptos/latest/leptos/attribute_interceptor/fn.AttributeInterceptor.html)

ดูรายละเอียดเพิ่มเติมได้ที่ [ตัวอย่าง `spread`](https://github.com/leptos-rs/leptos/blob/main/examples/spread/src/lib.rs)

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
