# การโหลดข้อมูลด้วยรีซอร์ส

รีซอร์สเป็นตัวห่อแบบรีแอกทีฟสำหรับงานแบบอะซิงโครนัส ซึ่งช่วยให้คุณผสาน `Future` แบบอะซิงโครนัส
เข้ากับระบบรีแอกทีฟแบบซิงโครนัสได้

รีซอร์สช่วยให้คุณโหลดข้อมูลแบบอะซิงก์บางอย่าง แล้วเข้าถึงข้อมูลนั้นได้แบบรีแอกทีฟทั้งในแบบ
ซิงโครนัสและอะซิงโครนัส คุณสามารถ `.await` รีซอร์สได้เหมือนกับ `Future` ทั่วไป ซึ่งจะติดตามมันให้
แต่คุณยังเข้าถึงรีซอร์สด้วย `.get()` และเมธอดเข้าถึงสัญญาณอื่นๆ ได้ด้วย ราวกับว่ารีซอร์สเป็น
สัญญาณที่คืนค่า `Some(T)` หากโหลดเสร็จแล้ว และ `None` หากยังคงรอดำเนินการอยู่

รีซอร์สมีสองรูปแบบหลัก: `Resource` และ `LocalResource` หากคุณใช้การเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR)
(ซึ่งหนังสือเล่มนี้จะกล่าวถึงในภายหลัง) คุณควรใช้ `Resource` เป็นค่าเริ่มต้น หากคุณใช้
การเรนเดอร์ฝั่งไคลเอนต์ (CSR) ร่วมกับ API ที่ไม่ใช่ `!Send` (อย่าง API ของเบราว์เซอร์หลายตัว)
หรือหากคุณใช้ SSR แต่มีงานอะซิงก์ที่ทำได้เฉพาะบนเบราว์เซอร์ (ตัวอย่างเช่น การเข้าถึง API ของ
เบราว์เซอร์แบบอะซิงก์) คุณก็ควรใช้ `LocalResource`

## รีซอร์สแบบโลคอล

`LocalResource::new()` รับอาร์กิวเมนต์เดียว: ฟังก์ชัน “ตัวดึงข้อมูล (fetcher)” ที่คืนค่า `Future`

`Future` นั้นอาจเป็นบล็อก `async` ผลลัพธ์จากการเรียก `async fn` หรือ `Future` อื่นๆ ของ Rust
ก็ได้ ฟังก์ชันนี้จะทำงานเหมือนสัญญาณอนุพัทธ์หรือโคลเชอร์รีแอกทีฟอื่นๆ ที่เราเห็นมาแล้ว: คุณสามารถ
อ่านสัญญาณภายในมันได้ และเมื่อใดที่สัญญาณเปลี่ยน ฟังก์ชันจะรันอีกครั้งเพื่อสร้าง `Future` ใหม่ให้รัน

```rust
// this count is our synchronous, local state
let (count, set_count) = signal(0);

// tracks `count`, and reloads by calling `load_data`
// whenever it changes
let async_data = LocalResource::new(move || load_data(count.get()));
```

การสร้างรีซอร์สจะเรียกฟังก์ชันดึงข้อมูลของมันทันทีและเริ่มโพลล์ `Future` การอ่านจากรีซอร์สจะคืนค่า
`None` จนกว่างานอะซิงก์จะเสร็จสิ้น ณ จุดนั้นมันจะแจ้งเตือนผู้ติดตามของมัน และจะกลายเป็น `Some(value)`

คุณยังสามารถ `.await` รีซอร์สได้ด้วย ซึ่งอาจดูเหมือนไม่มีประโยชน์—ทำไมคุณถึงต้องสร้างตัวห่อรอบ
`Future` แล้วกลับมา `.await` มันอีกล่ะ? เราจะเห็นคำตอบในบทถัดไป

## รีซอร์ส

หากคุณใช้ SSR ในกรณีส่วนใหญ่คุณควรใช้ `Resource` แทน `LocalResource`

API นี้แตกต่างออกไปเล็กน้อย `Resource::new()` รับฟังก์ชันสองตัวเป็นอาร์กิวเมนต์:

1. ฟังก์ชันต้นทาง (source function) ซึ่งบรรจุ “อินพุต” ไว้ อินพุตนี้จะถูกเมโมไมซ์ และเมื่อใดที่ค่าของมันเปลี่ยน ฟังก์ชันดึงข้อมูลก็จะถูกเรียก
2. ฟังก์ชันดึงข้อมูล (fetcher function) ซึ่งรับข้อมูลจากฟังก์ชันต้นทางและคืนค่า `Future`

ต่างจาก `LocalResource` ตรงที่ `Resource` จะซีเรียลไลซ์ค่าของมันจากเซิร์ฟเวอร์ไปยังไคลเอนต์
จากนั้นบนไคลเอนต์ เมื่อโหลดหน้าเพจครั้งแรก ค่าเริ่มต้นจะถูกดีซีเรียลไลซ์แทนที่จะรันงานอะซิงก์ซ้ำอีกครั้ง
สิ่งนี้สำคัญมากและมีประโยชน์อย่างยิ่ง: นั่นหมายความว่าแทนที่จะรอให้บันเดิล WASM ฝั่งไคลเอนต์
โหลดเสร็จและเริ่มรันแอปพลิเคชัน การโหลดข้อมูลก็เริ่มต้นขึ้นที่เซิร์ฟเวอร์แล้ว (จะมีรายละเอียด
เพิ่มเติมเกี่ยวกับเรื่องนี้ในบทต่อๆ ไป)

นี่ก็เป็นเหตุผลว่าทำไม API จึงถูกแบ่งออกเป็นสองส่วน: สัญญาณในฟังก์ชัน *source* จะถูกติดตาม
แต่สัญญาณใน *fetcher* จะไม่ถูกติดตาม เพราะวิธีนี้ช่วยให้รีซอร์สคงความสามารถในการเป็นรีแอกทีฟ
ได้โดยไม่ต้องรันฟังก์ชันดึงข้อมูลซ้ำอีกครั้งระหว่างการไฮเดรตครั้งแรกบนไคลเอนต์

นี่คือตัวอย่างเดิม แต่ใช้ `Resource` แทน `LocalResource`

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

รีซอร์สยังมีเมธอด `refetch()` ที่ช่วยให้คุณโหลดข้อมูลใหม่ได้ด้วยตัวเอง (ตัวอย่างเช่น
เมื่อตอบสนองต่อการคลิกปุ่ม)

หากต้องการสร้างรีซอร์สที่รันเพียงครั้งเดียว คุณสามารถใช้ `OnceResource` ซึ่งเพียงรับ `Future`
และเพิ่มการปรับปรุงประสิทธิภาพบางอย่างที่มาจากการรู้ว่ามันจะโหลดเพียงครั้งเดียว

```rust
let once = OnceResource::new(load_data(42));
```

## การเข้าถึงรีซอร์ส

ทั้ง `LocalResource` และ `Resource` ต่างอิมพลีเมนต์เมธอดเข้าถึงสัญญาณต่างๆ (`.read()`, `.with()`,
`.get()`) แต่คืนค่า `Option<T>` แทนที่จะเป็น `T` พวกมันจะเป็น `None` จนกว่าข้อมูลอะซิงก์จะโหลดเสร็จ

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
