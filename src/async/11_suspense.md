# ซัสเพนส์ (`<Suspense/>`)

ในบทที่แล้ว เราได้แสดงวิธีสร้างหน้าจอแสดงสถานะการโหลดแบบง่าย เพื่อแสดงคอมโพเนนต์สำรอง (fallback) ในระหว่างที่รีซอร์สกำลังโหลดข้อมูล

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

แต่ถ้าเรามีรีซอร์ส 2 ตัว และต้องการรอให้ทั้งคู่โหลดเสร็จก่อนล่ะ?

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

โค้ดแบบนี้ก็ไม่ได้แย่*ขนาดนั้น* แต่มันค่อนข้างน่ารำคาญ จะดีกว่าไหมถ้าเราสามารถกลับทิศทางของการควบคุม (inversion of control) ได้?

คอมโพเนนต์ [`<Suspense/>`](https://docs.rs/leptos/latest/leptos/suspense/fn.Suspense.html) ช่วยให้เราทำสิ่งนั้นได้อย่างตรงจุด โดยคุณเพียงส่งพร็อพ `fallback` และคอมโพเนนต์ลูก (children) ให้มัน ซึ่งภายในคอมโพเนนต์ลูกอย่างน้อยหนึ่งตัวมักจะมีการอ่านค่าจากรีซอร์ส การอ่านค่าจากรีซอร์สที่อยู่ "ใต้" `<Suspense/>` (นั่นคือภายในลูกตัวใดตัวหนึ่ง) จะทำการลงทะเบียนรีซอร์สนั้นเข้ากับ `<Suspense/>` โดยอัตโนมัติ หากยังคงรอให้รีซอร์สโหลดอยู่ มันจะแสดงผล `fallback` และเมื่อโหลดครบสมบูรณ์ทั้งหมดแล้ว จึงจะแสดงผลคอมโพเนนต์ลูก

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

ทุกครั้งที่มีรีซอร์สตัวใดตัวหนึ่งกำลังโหลดข้อมูลใหม่ ฟอลแบ็ก `"Loading..."` ก็จะกลับมาแสดงผลอีกครั้ง

การกลับทิศทางการควบคุมแบบนี้ช่วยให้การเพิ่มหรือลบลดรีซอร์สแต่ละตัวทำได้ง่ายขึ้นมาก เพราะคุณไม่ต้องมาคอยจัดการจับคู่เงื่อนไขด้วยตนเอง นอกจากนี้ ยังปลดล็อกการปรับปรุงประสิทธิภาพครั้งสำคัญในระหว่างการเรนเดอร์ฝั่งเซิร์ฟเวอร์ (SSR) ซึ่งเราจะพูดถึงกันในบทต่อ ๆ ไป

การใช้ `<Suspense/>` ยังเปิดโอกาสให้เราสามารถ `.await` รีซอร์สได้โดยตรง ซึ่งช่วยขจัดโค้ดซ้อนหลายชั้น (nesting) ในตัวอย่างข้างต้นออกไปได้ โดยประเภทข้อมูล `Suspend` ช่วยให้เราสร้าง `Future` ที่สามารถเรนเดอร์ลงในวิวได้โดยตรง:

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

`Suspend` ช่วยให้เราไม่ต้องมาคอยตรวจเช็กค่า null/None ของแต่ละรีซอร์สด้วยตนเอง และช่วยลดความซับซ้อนของโค้ดลงไปได้มาก

## `<Await/>`

หากคุณเพียงต้องการรอให้ `Future` ใด ๆ ทำงานเสร็จสิ้นก่อนที่จะทำการเรนเดอร์ คุณอาจพบว่าคอมโพเนนต์ `<Await/>` มีประโยชน์อย่างมากในการช่วยลดโค้ดแบบ boilerplate โดยแท้จริงแล้ว `<Await/>` เป็นการนำ `OnceResource` มารวมเข้ากับ `<Suspense/>` ที่ไม่มีฟอลแบ็กนั่นเอง

กล่าวอีกนัยหนึ่งคือ:

1. มันจะโพลล์ `Future` เพียงครั้งเดียวเท่านั้น และไม่ตอบสนองต่อการเปลี่ยนแปลงเชิงรีแอกทีฟใด ๆ
2. มันจะไม่เรนเดอร์สิ่งใดเลยจนกว่า `Future` จะทำงานเสร็จสิ้น
3. หลังจาก `Future` ทำงานเสร็จสิ้นแล้ว มันจะผูกข้อมูลที่ได้เข้ากับชื่อตัวแปรที่คุณกำหนด จากนั้นจึงเรนเดอร์คอมโพเนนต์ลูกโดยมีตัวแปรนั้นอยู่ในสโคป (scope)

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
