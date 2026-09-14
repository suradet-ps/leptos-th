# การโหลดข้อมูลด้วยรีซอร์ส

รีซอร์ส (Resource) เป็นตัวห่อหุ้มเชิงรีแอกทีฟ (reactive wrapper) สำหรับงานแบบอะซิงโครนัส ซึ่งช่วยให้คุณผสาน `Future` แบบอะซิงโครนัสเข้ากับระบบรีแอกทีฟแบบซิงโครนัสได้อย่างแนบเนียน

รีซอร์สช่วยให้คุณโหลดข้อมูลแบบอะซิงก์ แล้วเข้าถึงข้อมูลนั้นได้แบบรีแอกทีฟทั้งในรูปแบบซิงโครนัสและอะซิงโครนัส คุณสามารถ `.await` รีซอร์สได้เหมือนกับ `Future` ทั่วไป ซึ่งระบบจะคอยติดตาม (track) ค่าให้โดยอัตโนมัติ นอกจากนี้ คุณยังเข้าถึงรีซอร์สด้วย `.get()` และเมธอดเข้าถึงสัญญาณอื่น ๆ ได้เสมือนว่ารีซอร์สเป็นสัญญาณที่คืนค่า `Some(T)` เมื่อโหลดเสร็จแล้ว และคืนค่า `None` หากยังคงอยู่ระหว่างรอดำเนินการ (pending)

รีซอร์สมี 2 รูปแบบหลัก: `Resource` และ `LocalResource` หากคุณใช้การเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR) (ซึ่งหนังสือเล่มนี้จะกล่าวถึงในบทต่อ ๆ ไป) คุณควรเลือกใช้ `Resource` เป็นค่าเริ่มต้น แต่หากคุณใช้การเรนเดอร์ฝั่งไคลเอนต์ (CSR) ร่วมกับ API ที่ไม่เป็น `!Send` (เช่น Web API ของเบราว์เซอร์หลายตัว) หรือหากคุณใช้ SSR แต่มีงานอะซิงก์ที่ต้องทำเฉพาะบนเบราว์เซอร์เท่านั้น (เช่น การเข้าถึง API ของเบราว์เซอร์แบบอะซิงโครนัส) คุณก็ควรเลือกใช้ `LocalResource`

## รีซอร์สแบบโลคอล

`LocalResource::new()` รับอาร์กิวเมนต์เพียงตัวเดียว คือฟังก์ชัน "ตัวดึงข้อมูล" (fetcher function) ที่คืนค่าเป็น `Future`

`Future` ดังกล่าวอาจเป็นบล็อก `async`, ผลลัพธ์จากการเรียก `async fn` หรือ `Future` ชนิดใดก็ได้ของ Rust ฟังก์ชันนี้จะทำงานคล้ายกับสัญญาณอนุพัทธ์ (derived signal) หรือโคลเชอร์รีแอกทีฟอื่น ๆ ที่เราเคยเห็นมา: คุณสามารถอ่านสัญญาณที่อยู่ภายในนั้นได้ และเมื่อใดก็ตามที่สัญญาณตัวนั้นมีการเปลี่ยนแปลง ฟังก์ชันจะถูกรันซ้ำเพื่อสร้าง `Future` ตัวใหม่ขึ้นมาทำงาน

```rust
// this count is our synchronous, local state
let (count, set_count) = signal(0);

// tracks `count`, and reloads by calling `load_data`
// whenever it changes
let async_data = LocalResource::new(move || load_data(count.get()));
```

การสร้างรีซอร์สจะสั่งเรียกฟังก์ชันดึงข้อมูลทันทีและเริ่มโพลล์ (poll) `Future` นั้น การอ่านค่าจากรีซอร์สจะคืนค่าเป็น `None` จนกว่างานอะซิงก์จะทำงานเสร็จสิ้น เมื่อถึงจุดนั้นมันจะแจ้งเตือนผู้ติดตาม (subscribers) ทั้งหมด และเปลี่ยนค่าเป็น `Some(value)`

คุณยังสามารถใช้ `.await` กับรีซอร์สได้ด้วย ซึ่งอาจฟังดูไม่ค่อยสมเหตุสมผล—ทำไมเราต้องสร้างตัวห่อครอบ `Future` ขึ้นมาเพื่อที่จะ `.await` มันอีกรอบล่ะ? เดี๋ยวเราจะได้เห็นคำตอบกันในบทถัดไป

## รีซอร์ส

หากคุณใช้ SSR ในกรณีส่วนใหญ่คุณควรใช้ `Resource` แทนที่จะเป็น `LocalResource`

API ของตัวนี้จะแตกต่างกันเล็กน้อย โดย `Resource::new()` จะรับฟังก์ชันสองตัวเป็นอาร์กิวเมนต์:

1. ฟังก์ชันต้นทาง (source function) ซึ่งระบุ "อินพุต" โดยอินพุตนี้จะถูกเมโมไมซ์ (memoized) ไว้ และเมื่อใดก็ตามที่ค่าของมันเปลี่ยน ฟังก์ชันดึงข้อมูลก็จะถูกเรียกทำงาน
2. ฟังก์ชันดึงข้อมูล (fetcher function) ซึ่งจะรับข้อมูลที่ส่งต่อมาจากฟังก์ชันต้นทางแล้วคืนค่าเป็น `Future`

สิ่งที่แตกต่างจาก `LocalResource` คือ `Resource` จะทำการแปลงข้อมูลเป็นอนุกรม (serialize) จากเซิร์ฟเวอร์ส่งไปยังไคลเอนต์ จากนั้นบนฝั่งไคลเอนต์เมื่อโหลดหน้าเว็บครั้งแรก ค่าเริ่มต้นจะถูกดีซีเรียลไลซ์ (deserialize) นำมาใช้ทันที แทนที่จะต้องรันงานอะซิงก์ซ้ำอีกรอบ จุดนี้มีความสำคัญและเป็นประโยชน์อย่างยิ่ง: หมายความว่าแทนที่จะต้องรอให้บันเดิล WASM ฝั่งไคลเอนต์ดาวน์โหลดเสร็จแล้วจึงเริ่มรันแอปพลิเคชัน การโหลดข้อมูลนั้นได้เริ่มต้นขึ้นเรียบร้อยแล้วตั้งแต่ที่ฝั่งเซิร์ฟเวอร์ (เราจะอธิบายรายละเอียดเรื่องนี้เพิ่มเติมในบทต่อ ๆ ไป)

นี่จึงเป็นเหตุผลที่ทำไม API ถึงถูกแบ่งออกเป็นสองส่วน: สัญญาณในฟังก์ชัน *source* จะถูกติดตาม (tracked) แต่สัญญาณใน *fetcher* จะไม่ถูกติดตาม (untracked) เพราะวิธีนี้ช่วยให้รีซอร์สยังคงคุณสมบัติความเป็นรีแอกทีฟไว้ได้ โดยไม่จำเป็นต้องรันฟังก์ชันดึงข้อมูลซ้ำอีกครั้งในระหว่างขั้นตอนการไฮเดรชัน (hydration) ครั้งแรกบนไคลเอนต์

นี่คือตัวอย่างเดิม แต่เปลี่ยนมาใช้ `Resource` แทน `LocalResource`

```rust
// this count is our synchronous, local state
let (count, set_count) = signal(0);

// our resource
let async_data = Resource::new(
    move || count.get(),
    // every time `count` changes, this will run
    |count| load_data(count) 
);
```

รีซอร์สยังมีเมธอด `refetch()` ที่ช่วยให้คุณสั่งโหลดข้อมูลใหม่ได้ด้วยตนเอง (เช่น ตอบสนองต่อการคลิกปุ่ม)

หากต้องการสร้างรีซอร์สที่รันเพียงรอบเดียว คุณสามารถใช้ `OnceResource` ซึ่งรับเพียง `Future` ตัวเดียว และมีการเพิ่มการปรับปรุงประสิทธิภาพที่ได้จากการรู้ล่วงหน้าว่ามันจะโหลดเพียงครั้งเดียวเท่านั้น

```rust
let once = OnceResource::new(load_data(42));
```

## การเข้าถึงรีซอร์ส

ทั้ง `LocalResource` และ `Resource` ต่างก็อิมพลีเมนต์เมธอดเข้าถึงสัญญาณต่าง ๆ (`.read()`, `.with()`, `.get()`) แต่จะคืนค่าเป็น `Option<T>` แทนที่จะเป็น `T` โดยค่าจะเป็น `None` จนกว่าข้อมูลแบบอะซิงก์จะโหลดเสร็จสมบูรณ์

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/10-resource-0-7-q5xr9m?file=%2Fsrc%2Fmain.rs%3A7%2C30)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/10-resource-0-7-q5xr9m?file=%2Fsrc%2Fmain.rs%3A7%2C30" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use gloo_timers::future::TimeoutFuture;
use leptos::prelude::*;

// Here we define an async function
// This could be anything: a network request, database read, etc.
// Here, we just multiply a number by 10
async fn load_data(value: i32) -> i32 {
    // fake a one-second delay
    TimeoutFuture::new(1_000).await;
    value * 10
}

#[component]
pub fn App() -> impl IntoView {
    // this count is our synchronous, local state
    let (count, set_count) = signal(0);

    // tracks `count`, and reloads by calling `load_data`
    // whenever it changes
    let async_data = LocalResource::new(move || load_data(count.get()));

    // a resource will only load once if it doesn't read any reactive data
    let stable = LocalResource::new(|| load_data(1));

    // we can access the resource values with .get()
    // this will reactively return None before the Future has resolved
    // and update to Some(T) when it has resolved
    let async_result = move || {
        async_data
            .get()
            .map(|value| format!("Server returned {value:?}"))
            // This loading state will only show before the first load
            .unwrap_or_else(|| "Loading...".into())
    };

    view! {
        <button
            on:click=move |_| *set_count.write() += 1
        >
            "Click me"
        </button>
        <p>
            <code>"stable"</code>": " {move || stable.get()}
        </p>
        <p>
            <code>"count"</code>": " {count}
        </p>
        <p>
            <code>"async_value"</code>": "
            {async_result}
            <br/>
        </p>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
