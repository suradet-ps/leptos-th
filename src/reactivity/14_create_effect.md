# การตอบสนองต่อการเปลี่ยนแปลงด้วยเอฟเฟกต์

เราเดินทางมาถึงจุดนี้ได้โดยที่ยังไม่ได้เอ่ยถึงอีกครึ่งหนึ่งของระบบรีแอกทีฟเลย นั่นก็คือเอฟเฟกต์ (effects)

ระบบรีแอกทิวิตีทำงานประสานกันเป็นสองส่วนเสมอ: เมื่อค่ารีแอกทีฟแต่ละตัว (“สัญญาณ” หรือ signals) มีการอัปเดต มันจะคอยแจ้งเตือนไปยังชิ้นส่วนของโค้ดที่ขึ้นต่อกันกับพวกมัน (“เอฟเฟกต์” หรือ effects) ให้กลับมาทำงานอีกครั้ง ทั้งสองส่วนนี้ต่างต้องพึ่งพาอาศัยซึ่งกันและกัน หากปราศจากเอฟเฟกต์ สัญญาณก็อาจจะเปลี่ยนแปลงค่าอยู่ภายในระบบได้ แต่จะไม่สามารถส่งผลลัพธ์หรือเกิดปฏิสัมพันธ์กับโลกภายนอกได้เลย และในทางกลับกัน หากปราศจากสัญญาณ เอฟเฟกต์ก็จะรันเพียงครั้งแรกครั้งเดียวแล้วไม่รันอีก เพราะไม่มีค่ารีแอกทีฟใดให้คอยติดตามการเปลี่ยนแปลง เอฟเฟกต์จึงเปรียบเสมือน "ผลข้างเคียง" (side effects) ของระบบรีแอกทีฟอย่างแท้จริง ซึ่งมีหน้าที่หลักในการเชื่อมต่อและซิงโครไนซ์ระบบรีแอกทีฟเข้ากับโลกภายนอกที่ไม่เป็นรีแอกทีฟ

ตัวอย่างเช่น ระบบเรนเดอร์ของ Leptos ใช้เอฟเฟกต์เพื่อคอยอัปเดตส่วนต่าง ๆ ของ DOM เมื่อสัญญาณเปลี่ยนค่า นอกจากนี้ คุณยังสามารถสร้างเอฟเฟกต์ขึ้นมาเองเพื่อซิงโครไนซ์ระบบรีแอกทีฟเข้ากับโลกภายนอกในรูปแบบอื่น ๆ ได้อีกด้วย

ฟังก์ชัน [`Effect::new`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html) รับอาร์กิวเมนต์เป็นฟังก์ชันคลอเชอร์ โดยจะรันฟังก์ชันนี้ในรอบประมวลผลถัดไป (tick) ของระบบรีแอกทีฟ (ตัวอย่างเช่น หากคุณเรียกใช้ภายในคอมโพเนนต์ มันจะรัน_หลังจาก_ที่คอมโพเนนต์นั้นถูกเรนเดอร์เรียบร้อยแล้ว) หากคุณเข้าถึงค่าของสัญญาณรีแอกทีฟใด ๆ ภายในคลอเชอร์นั้น ระบบจะบันทึกไว้ว่าเอฟเฟกต์นี้ขึ้นต่อสัญญาณตัวดังกล่าว และเมื่อใดก็ตามที่สัญญาณตัวใดตัวหนึ่งที่เอฟเฟกต์ผูกพันอยู่มีการเปลี่ยนค่า เอฟเฟกต์นี้ก็จะถูกเรียกทำงานใหม่อีกครั้ง

```rust
let (a, set_a) = signal(0);
let (b, set_b) = signal(0);

Effect::new(move |_| {
  // immediately prints "Value: 0" and subscribes to `a`
  logging::log!("Value: {}", a.get());
});
```

ฟังก์ชันเอฟเฟกต์จะได้รับอาร์กิวเมนต์ตัวหนึ่ง ซึ่งเก็บค่าที่ฟังก์ชันส่งกลับมา (return) จากการรันในรอบก่อนหน้า โดยในการรันรอบแรกสุด ค่านี้จะเป็น `None`

โดยค่าเริ่มต้นแล้ว เอฟเฟกต์**จะไม่ทำงานบนฝั่งเซิร์ฟเวอร์** นั่นหมายความว่าคุณสามารถเรียกใช้ Web API เฉพาะของเบราว์เซอร์ภายในฟังก์ชันเอฟเฟกต์ได้อย่างปลอดภัยโดยไม่ต้องกังวลเรื่องการคอมไพล์ฝั่งเซิร์ฟเวอร์ แต่หากคุณต้องการให้เอฟเฟกต์ทำงานบนฝั่งเซิร์ฟเวอร์ด้วย ให้ใช้ฟังก์ชัน [`Effect::new_isomorphic`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html#method.new_isomorphic)

## การติดตามอัตโนมัติและดีเพนเดนซีแบบไดนามิก

หากคุณคุ้นเคยกับเฟรมเวิร์กอย่าง React คุณอาจสังเกตเห็นความแตกต่างสำคัญประการหนึ่ง นั่นคือ React และเฟรมเวิร์กในกลุ่มเดียวกันมักบังคับให้คุณต้องส่ง "dependency array" ซึ่งเป็นรายการตัวแปรที่ต้องระบุไว้อย่างชัดแจ้ง เพื่อบอกระบบว่าเอฟเฟกต์ควรรันซ้ำเมื่อใด

เนื่องจาก Leptos มีรากฐานมาจากการเขียนโปรแกรมเชิงปฏิกิริยาแบบซิงโครนัส (synchronous reactive programming) เราจึงไม่จำเป็นต้องมากำหนดรายการดีเพนเดนซีเหล่านี้ด้วยตัวเอง แต่ระบบจะคอยติดตามดีเพนเดนซีให้โดยอัตโนมัติ จากการตรวจสอบว่ามีสัญญาณตัวใดบ้างที่ถูกเรียกอ่านค่าภายในเอฟเฟกต์นั้น

สิ่งนี้ส่งผลดี 2 ประการ (ขออภัยหากดูเหมือนเล่นคำ) กล่าวคือ ดีเพนเดนซีจะมีลักษณะ:

1. **เป็นไปโดยอัตโนมัติ (Automatic)**: คุณไม่จำเป็นต้องคอยดูแลรักษา dependency array เอง หรือคอยพะวงว่าลืมใส่ตัวแปรไหนหรือไม่ เฟรมเวิร์กจะคอยตรวจจับเองว่าสัญญาณตัวใดส่งผลต่อการรันซ้ำของเอฟเฟกต์ และจัดการทั้งหมดให้โดยอัตโนมัติ
2. **เป็นแบบไดนามิก (Dynamic)**: รายการดีเพนเดนซีจะถูกล้างและอัปเดตใหม่ทุกรอบที่เอฟเฟกต์ทำงาน หากเอฟเฟกต์ของคุณมีเงื่อนไข (เช่น `if-else`) จะมีเพียงสัญญาณที่ถูกเรียกใช้ในกิ่ง (branch) ที่ทำงานอยู่ในรอบนั้นจริง ๆ เท่านั้นที่จะถูกติดตาม ซึ่งหมายความว่าเอฟเฟกต์จะรันซ้ำเฉพาะเมื่อจำเป็นจริง ๆ เท่านั้น

> หากแนวคิดนี้ฟังดูเหมือนเวทมนตร์ และคุณต้องการเจาะลึกว่าระบบติดตามดีเพนเดนซีอัตโนมัติทำงานเบื้องหลังอย่างไร [ลองดูวิดีโอนี้](https://www.youtube.com/watch?v=GWB3vTWeLd4) (ต้องขออภัยที่เสียงในคลิปอาจจะเบาไปสักหน่อย!)

## เอฟเฟกต์ในฐานะแอ็บสแตรกชันที่เกือบไร้ต้นทุน

แม้ว่าในเชิงเทคนิคระดับลึกที่สุด เอฟเฟกต์อาจจะไม่ใช่ "zero-cost abstraction" อย่างแท้จริง เพราะยังต้องใช้หน่วยความจำเพิ่มขึ้นเล็กน้อยและมีโครงสร้างคงอยู่ ณ ตอนรันไทม์ แต่ในมุมมองระดับการทำงานจริง (high-level) สำหรับภาระงานที่คุณทำอยู่ภายในเอฟเฟกต์ ไม่ว่าจะเป็นการเรียก API ที่ใช้ทรัพยากรสูงหรืองานอื่น ๆ เอฟเฟกต์ก็นับเป็นแอ็บสแตรกชันที่แทบไม่มี overhead ส่วนเกินเลย เพราะมันจะรันซ้ำให้น้อยครั้งที่สุดเท่าที่จำเป็นตามเงื่อนไขที่คุณกำหนดไว้จริง ๆ

ลองจินตนาการว่าเรากำลังพัฒนาซอฟต์แวร์ห้องแชท และต้องการให้ผู้ใช้เลือกแสดงชื่อเต็มหรือเฉพาะชื่อจริงได้ พร้อมกับแจ้งไปยังเซิร์ฟเวอร์ทุกครั้งที่ชื่อของพวกเขาเปลี่ยนแปลง:

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

หาก `use_last` มีค่าเป็น `true` เอฟเฟกต์ควรจะรันซ้ำเมื่อ `first`, `last` หรือ `use_last` มีการเปลี่ยนค่า แต่หากผู้ใช้สลับ `use_last` เป็น `false` การเปลี่ยนแปลงของ `last` ก็จะไม่ส่งผลต่อการแสดงผลชื่อเลย และในความเป็นจริง `last` จะถูกตัดออกจากรายการดีเพนเดนซีโดยอัตโนมัติ จนกว่า `use_last` จะถูกเปิดกลับมาเป็น `true` อีกครั้ง กลไกนี้ช่วยป้องกันไม่ให้ส่งคำขอที่ไม่จำเป็นไปยังเซิร์ฟเวอร์ แม้ว่าจะมีการแก้ไข `last` ไปหลายรอบในระหว่างที่ `use_last` ยังคงเป็น `false`

## จะสร้างเอฟเฟกต์ดีหรือไม่ดี?

เอฟเฟกต์มีไว้เพื่อซิงโครไนซ์ระบบรีแอกทีฟเข้ากับโลกภายนอกที่ไม่เป็นรีแอกทีฟ ไม่ใช่ใช้เพื่อซิงโครไนซ์ค่าระหว่างสองสัญญาณรีแอกทีฟด้วยกันเอง กล่าวอีกนัยหนึ่ง: การใช้เอฟเฟกต์เพื่อคอยอ่านค่าจากสัญญาณหนึ่ง แล้วนำไปสั่งอัปเดตลงในอีกสัญญาณหนึ่ง ไม่เคยเป็นแนวทางที่ดีเลย

หากคุณต้องการสร้างสัญญาณที่มีค่าขึ้นกับสัญญาณอื่น ๆ ให้เลือกใช้สัญญาณอนุพัทธ์ (derived signals) หรือ [`Memo`](https://docs.rs/leptos/latest/leptos/reactive/computed/struct.Memo.html) แทน การเขียนค่าลงสัญญาณภายในเอฟเฟกต์อาจไม่ได้ทำให้คอมพิวเตอร์ของคุณพัง แต่การใช้ derived signal หรือ memo นั้นย่อมดีกว่าเสมอ ทั้งในแง่ของทิศทางการไหลของข้อมูลที่ชัดเจน และในแง่ของประสิทธิภาพการทำงาน

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

หากคุณจำเป็นต้องซิงโครไนซ์ค่ารีแอกทีฟบางอย่างออกไปยังโลกภายนอกที่ไม่เป็นรีแอกทีฟ เช่น เว็บ API, คอนโซล, ระบบไฟล์ หรือ DOM การอัปเดตค่าลงในสัญญาณจากเหตุการณ์ภายนอกก็เป็นเรื่องที่เหมาะสม อย่างไรก็ตาม ในหลายกรณี คุณอาจพบว่าจริง ๆ แล้วคุณกำลังเขียนค่าลงสัญญาณจากภายในตัวตรวจจับเหตุการณ์ (event listener) หรือฟังก์ชันคอลแบ็ก ไม่ใช่จากภายในเอฟเฟกต์ สำหรับกรณีเหล่านี้ ขอแนะนำให้ลองดูไลบรารี [`leptos-use`](https://leptos-use.rs/) ว่ามี reactive primitives สำเร็จรูปที่ห่อหุ้มสิ่งที่คุณต้องการไว้อยู่แล้วหรือไม่!

> หากคุณต้องการศึกษาเพิ่มเติมว่าเมื่อใดที่ควรและไม่ควรใช้ `Effect::new` (หรือ `create_effect` ในเวอร์ชันก่อนหน้า) [ลองดูวิดีโอนี้](https://www.youtube.com/watch?v=aQOFJQ2JkvQ) เพื่อทำความเข้าใจให้ลึกซึ้งยิ่งขึ้น!

## เอฟเฟกต์และการเรนเดอร์

เราสามารถเรียนรู้การทำงานของ Leptos มาได้ไกลขนาดนี้โดยไม่ต้องพูดถึงเอฟเฟกต์ ก็เพราะว่าเอฟเฟกต์ได้ถูกผนวกไว้ภายในตัวเรนเดอร์ DOM ของ Leptos อยู่แล้วโดยอัตโนมัติ เราได้เห็นแล้วว่าเพียงแค่เราสร้างสัญญาณขึ้นมาแล้วส่งเข้าไปในมาโคร `view` ระบบก็จะคอยอัปเดตโหนด DOM ที่เกี่ยวข้องให้โดยอัตโนมัติทุกครั้งที่สัญญาณมีการเปลี่ยนแปลง:

```rust
let (count, set_count) = signal(0);

view! {
    <p>{count}</p>
}
```

การทำงานนี้เกิดขึ้นได้เพราะเฟรมเวิร์กจะสร้างเอฟเฟกต์ขึ้นมาครอบการอัปเดตนี้ไว้ให้เบื้องหลัง คุณสามารถจินตนาการได้ว่า Leptos แปลงโค้ดวิวข้างต้นออกมาในลักษณะประมาณนี้:

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

ทุกครั้งที่ `count` มีการอัปเดต เอฟเฟกต์นี้ก็จะรันซ้ำเพื่ออัปเดตข้อความบน DOM นี่คือกลไกเบื้องหลังที่ทำให้เกิดการอัปเดต DOM แบบละเอียด (fine-grained reactive DOM updates) ขึ้นมา

## การติดตามอย่างชัดเจนด้วย `Effect::watch()`

นอกจาก `Effect::new()` แล้ว Leptos ยังมีฟังก์ชัน [`Effect::watch()`](https://docs.rs/leptos/latest/leptos/reactive/effect/struct.Effect.html#method.watch) ซึ่งช่วยให้คุณสามารถแยกส่วนการติดตามดีเพนเดนซี ออกจากการตอบสนองต่อการเปลี่ยนแปลงได้อย่างชัดเจน โดยสามารถกำหนดชุดค่าที่ต้องการให้เฝ้าติดตามได้อย่างเจาะจง

`watch` รับอาร์กิวเมนต์ 3 ตัว ได้แก่ `dependency_fn` ซึ่งจะถูกติดตามแบบรีแอกทีฟ ส่วน `handler` และ `immediate` จะไม่ถูกนำไปติดตาม เมื่อใดก็ตามที่ค่าซึ่งคืนจาก `dependency_fn` มีการเปลี่ยนแปลง ฟังก์ชัน `handler` จะถูกเรียกทำงาน และหาก `immediate` มีค่าเป็น `false` ฟังก์ชัน `handler` จะเริ่มทำงานเฉพาะเมื่อตรวจพบการเปลี่ยนแปลงของสัญญาณใน `dependency_fn` เป็นครั้งแรกเท่านั้น นอกจากนี้ `watch` จะคืนค่ากลับมาเป็น `Effect` ซึ่งคุณสามารถเรียกใช้เมธอด `.stop()` เพื่อสั่งหยุดการติดตามดีเพนเดนซีได้ทุกเมื่อ

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
