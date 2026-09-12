# ซัสเพนส์ (`<Suspense/>`)

ในบทที่แล้ว เราได้แสดงวิธีสร้างหน้าจอโหลดแบบง่ายเพื่อแสดงฟอลแบ็กบางอย่างระหว่างที่
รีซอร์สกำลังโหลด

```rust
let (count, set_count) = signal(0);
let once = Resource::new(move || count.get(), |count| async move { load_a(count).await });

view! {
    <h1>"My Data"</h1>
    {move || match once.get() {
        None => view! { <p>"Loading..."</p> }.into_any(),
        Some(data) => view! { <ShowData data/> }.into_any()
    }}
}
```

แต่ถ้าเรามีรีซอร์สสองตัวและต้องการรอให้ทั้งคู่โหลดเสร็จล่ะ?

```rust
let (count, set_count) = signal(0);
let (count2, set_count2) = signal(0);
let a = Resource::new(move || count.get(), |count| async move { load_a(count).await });
let b = Resource::new(move || count2.get(), |count| async move { load_b(count).await });

view! {
    <h1>"My Data"</h1>
    {move || match (a.get(), b.get()) {
        (Some(a), Some(b)) => view! {
            <ShowA a/>
            <ShowA b/>
        }.into_any(),
        _ => view! { <p>"Loading..."</p> }.into_any()
    }}
}
```

แบบนี้ก็ไม่ได้แย่_ขนาดนั้น_ แต่มันค่อนข้างน่ารำคาญ จะเป็นอย่างไรถ้าเราสลับทิศทาง
ของการควบคุมได้?

คอมโพเนนต์ [`<Suspense/>`](https://docs.rs/leptos/latest/leptos/suspense/fn.Suspense.html)
ช่วยให้เราทำอย่างนั้นได้เลย คุณส่งพร็อพ `fallback` และ children ให้มัน โดยหนึ่งตัวหรือมากกว่า
ในนั้นมักเกี่ยวข้องกับการอ่านจากรีซอร์ส การอ่านจากรีซอร์ส “ใต้” `<Suspense/>` (กล่าวคือ
ใน children ตัวใดตัวหนึ่งของมัน) จะลงทะเบียนรีซอร์สนั้นกับ `<Suspense/>` หากมันยังรอให้
รีซอร์สโหลดอยู่ มันจะแสดง `fallback` เมื่อโหลดครบทั้งหมดแล้ว มันจะแสดง children

```rust
let (count, set_count) = signal(0);
let (count2, set_count2) = signal(0);
let a = Resource::new(count, |count| async move { load_a(count).await });
let b = Resource::new(count2, |count| async move { load_b(count).await });

view! {
    <h1>"My Data"</h1>
    <Suspense
        fallback=move || view! { <p>"Loading..."</p> }
    >
        <h2>"My Data"</h2>
        <h3>"A"</h3>
        {move || {
            a.get()
                .map(|a| view! { <ShowA a/> })
        }}
        <h3>"B"</h3>
        {move || {
            b.get()
                .map(|b| view! { <ShowB b/> })
        }}
    </Suspense>
}
```

ทุกครั้งที่รีซอร์สตัวใดตัวหนึ่งกำลังโหลดใหม่ ฟอลแบ็ก `"Loading..."` ก็จะปรากฏขึ้นอีกครั้ง

การกลับทิศทางของการควบคุมแบบนี้ทำให้การเพิ่มหรือลบรีซอร์สแต่ละตัวง่ายขึ้น เพราะคุณ
ไม่ต้องจัดการจับคู่ด้วยตัวเอง มันยังปลดล็อกการปรับปรุงประสิทธิภาพครั้งใหญ่ระหว่าง
การเรนเดอร์ฝั่งเซิร์ฟเวอร์ ซึ่งเราจะพูดถึงในบทต่อๆ ไป

การใช้ `<Suspense/>` ยังมอบวิธีที่มีประโยชน์ในการ `.await` รีซอร์สโดยตรง ช่วยให้เรา
กำจัดชั้นของการซ้อนกันในตัวอย่างข้างต้นได้ ชนิด `Suspend` ช่วยให้เราสร้าง `Future`
ที่เรนเดอร์ได้ ซึ่งนำไปใช้ในวิวได้:

```rust
view! {
    <h1>"My Data"</h1>
    <Suspense
        fallback=move || view! { <p>"Loading..."</p> }
    >
        <h2>"My Data"</h2>
        {move || Suspend::new(async move {
            let a = a.await;
            let b = b.await;
            view! {
                <h3>"A"</h3>
                <ShowA a/>
                <h3>"B"</h3>
                <ShowB b/>
            }
        })}
    </Suspense>
}
```

`Suspend` ช่วยให้เราเลี่ยงการตรวจสอบค่า null ของรีซอร์สแต่ละตัว และลดความซับซ้อน
เพิ่มเติมออกจากโค้ด

## `<Await/>`

หากคุณเพียงแค่ต้องการรอให้ `Future` บางตัวโหลดเสร็จก่อนเรนเดอร์ คุณอาจพบว่าคอมโพเนนต์
`<Await/>` ช่วยลดโค้ดซ้ำซาก (boilerplate) ได้ `<Await/>` โดยพื้นฐานคือการรวม
`OnceResource` เข้ากับ `<Suspense/>` ที่ไม่มีฟอลแบ็ก

กล่าวอีกนัยหนึ่ง:

1. มันโพลล์ `Future` เพียงครั้งเดียว และไม่ตอบสนองต่อการเปลี่ยนแปลงแบบรีแอกทีฟใดๆ
2. มันไม่เรนเดอร์อะไรเลยจนกว่า `Future` จะโหลดเสร็จ
3. หลังจาก `Future` โหลดเสร็จ มันจะผูกข้อมูลของมันเข้ากับชื่อตัวแปรที่คุณเลือก แล้วเรนเดอร์ children โดยมีตัวแปรนั้นอยู่ในสโคป

```rust
async fn fetch_monkeys(monkey: i32) -> i32 {
    // maybe this didn't need to be async
    monkey * 2
}
view! {
    <Await
        // `future` provides the `Future` to be resolved
        future=fetch_monkeys(3)
        // the data is bound to whatever variable name you provide
        let:data
    >
        // you receive the data by reference and can use it in your view here
        <p>{*data} " little monkeys, jumping on the bed."</p>
    </Await>
}
```

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/11-suspense-0-7-sr2srk?file=%2Fsrc%2Fmain.rs%3A1%2C1-55%2C1)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/11-suspense-0-7-sr2srk?file=%2Fsrc%2Fmain.rs%3A1%2C1-55%2C1" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use gloo_timers::future::TimeoutFuture;
use leptos::prelude::*;

async fn important_api_call(name: String) -> String {
    TimeoutFuture::new(1_000).await;
    name.to_ascii_uppercase()
}

#[component]
pub fn App() -> impl IntoView {
    let (name, set_name) = signal("Bill".to_string());

    // this will reload every time `name` changes
    let async_data = LocalResource::new(move || important_api_call(name.get()));

    view! {
        <input
            on:change:target=move |ev| {
                set_name.set(ev.target().value());
            }
            prop:value=name
        />
        <p><code>"name:"</code> {name}</p>
        <Suspense
            // the fallback will show whenever a resource
            // read "under" the suspense is loading
            fallback=move || view! { <p>"Loading..."</p> }
        >
            // Suspend allows you use to an async block in the view
            <p>
                "Your shouting name is "
                {move || Suspend::new(async move {
                    async_data.await
                })}
            </p>
        </Suspense>
        <Suspense
            // the fallback will show whenever a resource
            // read "under" the suspense is loading
            fallback=move || view! { <p>"Loading..."</p> }
        >
            // the children will be rendered once initially,
            // and then whenever any resources has been resolved
            <p>
                "Which should be the same as... "
                {move || async_data.get().as_deref().map(ToString::to_string)}
            </p>
        </Suspense>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
