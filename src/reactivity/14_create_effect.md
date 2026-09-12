# การตอบสนองต่อการเปลี่ยนแปลงด้วยเอฟเฟกต์

เรามาไกลถึงเพียงนี้โดยยังไม่ได้กล่าวถึงครึ่งหนึ่งของระบบรีแอกทีฟเลย นั่นคือเอฟเฟกต์

รีแอกทิวิตีทำงานเป็นสองครึ่ง: การอัปเดตค่ารีแอกทีฟแต่ละตัว (“สัญญาณ”) จะแจ้งให้ชิ้นส่วนโค้ดที่ขึ้นกับพวกมัน (“เอฟเฟกต์”) รู้ว่าต้องรันอีกครั้ง สองครึ่งของระบบรีแอกทีฟนี้พึ่งพาอาศัยกัน หากไม่มีเอฟเฟกต์ สัญญาณก็สามารถเปลี่ยนแปลงภายในระบบรีแอกทีฟได้ แต่จะไม่ถูกสังเกตเห็นในลักษณะที่ปฏิสัมพันธ์กับโลกภายนอกเลย หากไม่มีสัญญาณ เอฟเฟกต์ก็จะรันเพียงครั้งเดียวและไม่รันอีก เพราะไม่มีค่าที่สังเกตได้ให้ติดตาม เอฟเฟกต์เป็น “ไซด์เอฟเฟกต์” ของระบบรีแอกทีฟอย่างแท้จริง นั่นคือ พวกมันมีอยู่เพื่อซิงโครไนซ์ระบบรีแอกทีฟกับโลกภายนอกที่ไม่รีแอกทีฟ

ตัวเรนเดอร์ใช้เอฟเฟกต์เพื่ออัปเดตส่วนต่างๆ ของ DOM เพื่อตอบสนองต่อการเปลี่ยนแปลงของสัญญาณ คุณสามารถสร้างเอฟเฟกต์ของคุณเองเพื่อซิงโครไนซ์ระบบรีแอกทีฟกับโลกภายนอกในรูปแบบอื่นๆ ได้

[`Effect::new`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html) รับฟังก์ชันเป็นอาร์กิวเมนต์ของมัน โดยจะรันฟังก์ชันนี้ใน “ทิก” (tick) ถัดไปของระบบรีแอกทีฟ (ตัวอย่างเช่น หากคุณใช้มันในคอมโพเนนต์ มันจะรัน_หลัง_จากที่คอมโพเนนต์นั้นถูกเรนเดอร์แล้ว) หากคุณเข้าถึงสัญญาณรีแอกทีฟใดๆ ภายในฟังก์ชันนั้น มันจะบันทึกว่าเอฟเฟกต์นั้นขึ้นกับสัญญาณตัวนั้น เมื่อใดก็ตามที่สัญญาณตัวใดตัวหนึ่งที่เอฟเฟกต์ขึ้นอยู่กับมันเปลี่ยน เอฟเฟกต์ก็จะรันอีกครั้ง

```rust
let (a, set_a) = signal(0);
let (b, set_b) = signal(0);

Effect::new(move |_| {
  // immediately prints "Value: 0" and subscribes to `a`
  logging::log!("Value: {}", a.get());
});
```

ฟังก์ชันเอฟเฟกต์จะถูกเรียกพร้อมอาร์กิวเมนต์ที่มีค่าที่มันคืนมาในการรันครั้งก่อนหน้า ในการรันครั้งแรก ค่านี้คือ `None`

โดยค่าเริ่มต้น เอฟเฟกต์**จะไม่รันบนเซิร์ฟเวอร์** ซึ่งหมายความว่าคุณสามารถเรียก API เฉพาะเบราว์เซอร์ภายในฟังก์ชันเอฟเฟกต์ได้โดยไม่เกิดปัญหา หากคุณต้องการให้เอฟเฟกต์รันบนเซิร์ฟเวอร์ ให้ใช้ [`Effect::new_isomorphic`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html#method.new_isomorphic)

## การติดตามอัตโนมัติและดีเพนเดนซีแบบไดนามิก

หากคุณคุ้นเคยกับเฟรมเวิร์กอย่าง React คุณอาจสังเกตเห็นความแตกต่างสำคัญประการหนึ่ง React และเฟรมเวิร์กที่คล้ายกันมักกำหนดให้คุณส่ง “อาร์เรย์ดีเพนเดนซี” ซึ่งเป็นชุดตัวแปรที่ระบุชัดเจนว่าตัวแปรใดกำหนดว่าเอฟเฟกต์ควรจะรันซ้ำเมื่อใด

เนื่องจาก Leptos มาจากสายของการเขียนโปรแกรมแบบซิงโครนัสรีแอกทีฟ เราจึงไม่จำเป็นต้องมีรายการดีเพนเดนซีที่ระบุชัดเจนนี้ แต่เราจะติดตามดีเพนเดนซีโดยอัตโนมัติ โดยดูจากสัญญาณตัวใดบ้างที่ถูกเข้าถึงภายในเอฟเฟกต์

เรื่องนี้มีสองเอฟเฟกต์ (ไม่ได้ตั้งใจเล่นคำ) ดีเพนเดนซีนั้น:

1. **อัตโนมัติ**: คุณไม่จำเป็นต้องดูแลรักษารายการดีเพนเดนซี หรือกังวลว่าอะไรควรหรือไม่ควรถูกรวมไว้ เฟรมเวิร์กจะติดตามเองว่าสัญญาณตัวใดอาจทำให้เอฟเฟกต์รันซ้ำ และจัดการให้คุณ
2. **ไดนามิก**: รายการดีเพนเดนซีจะถูกล้างและอัปเดตทุกครั้งที่เอฟเฟกต์รัน หากเอฟเฟกต์ของคุณมีเงื่อนไข (ตัวอย่างเช่น) จะมีเพียงสัญญาณที่ถูกใช้ในสาขาปัจจุบันเท่านั้นที่ถูกติดตาม ซึ่งหมายความว่าเอฟเฟกต์จะรันซ้ำน้อยที่สุดเท่าที่จำเป็นจริงๆ

> หากเรื่องนี้ฟังดูเหมือนเวทมนตร์ และหากคุณอยากเจาะลึกว่าการติดตามดีเพนเดนซีอัตโนมัติทำงานอย่างไร [ลองดูวิดีโอนี้](https://www.youtube.com/watch?v=GWB3vTWeLd4) (ขออภัยที่เสียงเบา!)

## เอฟเฟกต์ในฐานะแอ็บสแตรกชันที่เกือบไร้ต้นทุน

แม้ว่าพวกมันจะไม่ใช่ “แอ็บสแตรกชันไร้ต้นทุน” ในความหมายทางเทคนิคที่สุด เพราะต้องใช้หน่วยความจำเพิ่มขึ้นบ้างและมีอยู่จริงในขณะรันไทม์ เป็นต้น แต่ในมุมมองที่สูงขึ้น จากมุมมองของงานที่คุณทำอยู่ภายในเอฟเฟกต์ ไม่ว่าจะเป็นการเรียก API ที่มีค่าใช้จ่ายสูงหรืองานอื่นๆ เอฟเฟกต์ถือเป็นแอ็บสแตรกชันที่แทบไม่มีต้นทุน พวกมันจะรันซ้ำน้อยที่สุดเท่าที่จำเป็นจริงๆ เมื่อพิจารณาจากวิธีที่คุณอธิบายมันไว้

ลองจินตนาการว่าผมกำลังสร้างซอฟต์แวร์แชทแบบใดแบบหนึ่ง และผมต้องการให้ผู้คนสามารถแสดงชื่อเต็มของตน หรือแค่ชื่อต้น และแจ้งเซิร์ฟเวอร์ทุกครั้งที่ชื่อของพวกเขาเปลี่ยน:

```rust
let (first, set_first) = signal(String::new());
let (last, set_last) = signal(String::new());
let (use_last, set_use_last) = signal(true);

// this will add the name to the log
// any time one of the source signals changes
Effect::new(move |_| {
    logging::log!(
        "{}", if use_last.get() {
            format!("{} {}", first.get(), last.get())
        } else {
            first.get()
        },
    )
});
```

หาก `use_last` เป็น `true` เอฟเฟกต์ควรจะรันซ้ำทุกครั้งที่ `first`, `last` หรือ `use_last` เปลี่ยน แต่ถ้าผมสลับ `use_last` เป็น `false` การเปลี่ยนแปลงของ `last` จะไม่ทำให้ชื่อเต็มเปลี่ยนเลย ที่จริงแล้ว `last` จะถูกนำออกจากรายการดีเพนเดนซีจนกว่า `use_last` จะถูกสลับอีกครั้ง เรื่องนี้ช่วยไม่ให้เราส่งคำขอที่ไม่จำเป็นหลายครั้งไปยัง API หากผมเปลี่ยน `last` หลายครั้งในขณะที่ `use_last` ยังเป็น `false`

## จะสร้างเอฟเฟกต์ดีหรือไม่ดี?

เอฟเฟกต์มีไว้เพื่อซิงโครไนซ์ระบบรีแอกทีฟกับโลกภายนอกที่ไม่รีแอกทีฟ ไม่ใช่เพื่อซิงโครไนซ์ระหว่างค่ารีแอกทีฟที่ต่างกัน กล่าวอีกนัยหนึ่ง: การใช้เอฟเฟกต์เพื่ออ่านค่าจากสัญญาณหนึ่งแล้วตั้งค่าลงในอีกสัญญาณหนึ่งนั้นไม่เคยเป็นวิธีที่เหมาะสมที่สุด

หากคุณต้องนิยามสัญญาณที่ขึ้นกับค่าของสัญญาณอื่นๆ ให้ใช้สัญญาณอนุพัทธ์หรือ [`Memo`](https://docs.rs/leptos/latest/leptos/reactive/computed/struct.Memo.html) การเขียนค่าลงในสัญญาณภายในเอฟเฟกต์ไม่ใช่จุดจบของโลก และไม่ทำให้คอมพิวเตอร์ของคุณลุกเป็นไฟ แต่สัญญาณอนุพัทธ์หรือเมโมย่อมดีกว่าเสมอ ไม่เพียงเพราะโฟลว์ข้อมูลชัดเจน แต่ยังเพราะประสิทธิภาพดีกว่าด้วย

```rust
let (a, set_a) = signal(0);

// ⚠️ not great
let (b, set_b) = signal(0);
Effect::new(move |_| {
    set_b.set(a.get() * 2);
});

// ✅ woo-hoo!
let b = move || a.get() * 2;
```

หากคุณต้องซิงโครไนซ์ค่ารีแอกทีฟบางอย่างกับโลกภายนอกที่ไม่รีแอกทีฟ เช่น เว็บ API, คอนโซล, ระบบไฟล์ หรือ DOM การเขียนค่าลงในสัญญาณภายในเอฟเฟกต์ก็เป็นวิธีที่ดีในการทำเช่นนั้น อย่างไรก็ตาม ในหลายกรณี คุณจะพบว่าจริงๆ แล้วคุณกำลังเขียนค่าลงในสัญญาณภายในตัวรับฟังเหตุการณ์หรืออะไรทำนองนั้น ไม่ใช่ภายในเอฟเฟกต์ ในกรณีเหล่านี้ คุณควรดู [`leptos-use`](https://leptos-use.rs/) ว่ามันมีพรีมิทีฟห่อหุ้มแบบรีแอกทีฟสำหรับทำสิ่งนั้นอยู่แล้วหรือไม่!

> หากคุณอยากทราบข้อมูลเพิ่มเติมว่าควรและไม่ควรใช้ `create_effect` เมื่อใด [ลองดูวิดีโอนี้](https://www.youtube.com/watch?v=aQOFJQ2JkvQ) เพื่อพิจารณาให้ลึกซึ้งยิ่งขึ้น!

## เอฟเฟกต์และการเรนเดอร์

เราเดินทางมาไกลถึงเพียงนี้โดยไม่พูดถึงเอฟเฟกต์ เพราะมันถูกสร้างไว้ในตัวเรนเดอร์ DOM ของ Leptos เราได้เห็นแล้วว่าคุณสามารถสร้างสัญญาณและส่งมันเข้าไปในมาโคร `view` แล้วมันจะอัปเดตโหนด DOM ที่เกี่ยวข้องทุกครั้งที่สัญญาณเปลี่ยน:

```rust
let (count, set_count) = signal(0);

view! {
    <p>{count}</p>
}
```

สิ่งนี้ทำงานได้เพราะเฟรมเวิร์กสร้างเอฟเฟกต์ที่ห่อหุ้มการอัปเดตนี้ไว้ คุณสามารถจินตนาการได้ว่า Leptos แปลวิวนี้เป็นอะไรทำนองนี้:

```rust
let (count, set_count) = signal(0);

// create a DOM element
let document = leptos::document();
let p = document.create_element("p").unwrap();

// create an effect to reactively update the text
Effect::new(move |prev_value| {
    // first, access the signal’s value and convert it to a string
    let text = count.get().to_string();

    // if this is different from the previous value, update the node
    if prev_value != Some(text) {
        p.set_text_content(&text);
    }

    // return this value so we can memoize the next update
    text
});
```

ทุกครั้งที่ `count` ถูกอัปเดต เอฟเฟกต์นี้จะรันซ้ำ นี่คือสิ่งที่ทำให้เกิดการอัปเดต DOM แบบรีแอกทีฟและแบบละเอียด

## การติดตามอย่างชัดเจนด้วย `Effect::watch()`

นอกจาก `Effect::new()` แล้ว Leptos ยังมีฟังก์ชัน [`Effect::watch()`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html#method.watch) ซึ่งใช้แยกการติดตามออกจากการตอบสนองต่อการเปลี่ยนแปลงได้ โดยส่งชุดค่าที่ต้องการติดตามเข้าไปอย่างชัดเจน

`watch` รับอาร์กิวเมนต์สามตัว อาร์กิวเมนต์ `dependency_fn` จะถูกติดตามแบบรีแอกทีฟ ส่วน `handler` และ `immediate` จะไม่ถูกติดตาม เมื่อใดก็ตามที่ `dependency_fn` เปลี่ยน `handler` จะถูกรัน หาก `immediate` เป็น false `handler` จะรันเฉพาะหลังจากตรวจพบการเปลี่ยนแปลงครั้งแรกของสัญญาณใดๆ ที่ถูกเข้าถึงใน `dependency_fn` เท่านั้น `watch` คืนค่าเป็น `Effect` ซึ่งสามารถเรียกด้วย `.stop()` เพื่อหยุดติดตามดีเพนเดนซีได้

```rust
let (num, set_num) = signal(0);

let effect = Effect::watch(
    move || num.get(),
    move |num, prev_num, _| {
        leptos::logging::log!("Number: {}; Prev: {:?}", num, prev_num);
    },
    false,
);

set_num.set(1); // > "Number: 1; Prev: Some(0)"

effect.stop(); // stop watching

set_num.set(2); // (nothing happens)
```

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/14-effect-0-7-fxpy2d?file=%2Fsrc%2Fmain.rs%3A21%2C28&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  กรุณาเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/14-effect-0-7-fxpy2d?file=%2Fsrc%2Fmain.rs%3A21%2C28&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::html::Input;
use leptos::prelude::*;

#[derive(Copy, Clone)]
struct LogContext(RwSignal<Vec<String>>);

#[component]
fn App() -> impl IntoView {
    // Just making a visible log here
    // You can ignore this...
    let log = RwSignal::<Vec<String>>::new(vec![]);
    let logged = move || log.get().join("\n");

    // the newtype pattern isn't *necessary* here but is a good practice
    // it avoids confusion with other possible future `RwSignal<Vec<String>>` contexts
    // and makes it easier to refer to it
    provide_context(LogContext(log));

    view! {
        <CreateAnEffect/>
        <pre>{logged}</pre>
    }
}

#[component]
fn CreateAnEffect() -> impl IntoView {
    let (first, set_first) = signal(String::new());
    let (last, set_last) = signal(String::new());
    let (use_last, set_use_last) = signal(true);

    // this will add the name to the log
    // any time one of the source signals changes
    Effect::new(move |_| {
        log(if use_last.get() {
            let first = first.read();
            let last = last.read();
            format!("{first} {last}")
        } else {
            first.get()
        })
    });

    view! {
        <h1>
            <code>"create_effect"</code>
            " Version"
        </h1>
        <form>
            <label>
                "First Name"
                <input
                    type="text"
                    name="first"
                    prop:value=first
                    on:change:target=move |ev| set_first.set(ev.target().value())
                />
            </label>
            <label>
                "Last Name"
                <input
                    type="text"
                    name="last"
                    prop:value=last
                    on:change:target=move |ev| set_last.set(ev.target().value())
                />
            </label>
            <label>
                "Show Last Name"
                <input
                    type="checkbox"
                    name="use_last"
                    prop:checked=use_last
                    on:change:target=move |ev| set_use_last.set(ev.target().checked())
                />
            </label>
        </form>
    }
}

#[component]
fn ManualVersion() -> impl IntoView {
    let first = NodeRef::<Input>::new();
    let last = NodeRef::<Input>::new();
    let use_last = NodeRef::<Input>::new();

    let mut prev_name = String::new();
    let on_change = move |_| {
        log("      listener");
        let first = first.get().unwrap();
        let last = last.get().unwrap();
        let use_last = use_last.get().unwrap();
        let this_one = if use_last.checked() {
            format!("{} {}", first.value(), last.value())
        } else {
            first.value()
        };

        if this_one != prev_name {
            log(&this_one);
            prev_name = this_one;
        }
    };

    view! {
        <h1>"Manual Version"</h1>
        <form on:change=on_change>
            <label>"First Name" <input type="text" name="first" node_ref=first/></label>
            <label>"Last Name" <input type="text" name="last" node_ref=last/></label>
            <label>
                "Show Last Name" <input type="checkbox" name="use_last" checked node_ref=use_last/>
            </label>
        </form>
    }
}

fn log(msg: impl std::fmt::Display) {
    let log = use_context::<LogContext>().unwrap().0;
    log.update(|log| log.push(msg.to_string()));
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
