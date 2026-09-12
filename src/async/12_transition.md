# ทรานซิชัน (`<Transition/>`)

คุณจะสังเกตได้ในตัวอย่าง `<Suspense/>` ว่า หากคุณโหลดข้อมูลซ้ำๆ มันจะกะพริบกลับไปที่
`"Loading..."` อยู่เรื่อยๆ บางครั้งแบบนี้ก็โอเค แต่ในบางครั้ง ก็มี
[`<Transition/>`](https://docs.rs/leptos/latest/leptos/suspense/fn.Transition.html) ให้ใช้

`<Transition/>` ทำงานเหมือน `<Suspense/>` ทุกประการ แต่แทนที่จะฟอลแบ็กทุกครั้ง
มันจะแสดงฟอลแบ็กเฉพาะครั้งแรกเท่านั้น ในการโหลดครั้งต่อๆ ไปทั้งหมด มันจะแสดงข้อมูลเก่า
ต่อไปจนกว่าข้อมูลใหม่จะพร้อม สิ่งนี้มีประโยชน์มากในการป้องกันเอฟเฟกต์การกะพริบ
และช่วยให้ผู้ใช้โต้ตอบกับแอปพลิเคชันของคุณต่อไปได้

ตัวอย่างนี้แสดงวิธีสร้างรายชื่อผู้ติดต่อแบบแท็บอย่างง่ายด้วย `<Transition/>` เมื่อคุณ
เลือกแท็บใหม่ มันจะแสดงผู้ติดต่อคนปัจจุบันต่อไปจนกว่าข้อมูลใหม่จะโหลดเสร็จ
ซึ่งให้ประสบการณ์ผู้ใช้ที่ดีกว่าการฟอลแบ็กกลับไปที่ข้อความกำลังโหลดอยู่ตลอดเวลาได้มาก

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/12-transition-0-7-ln2hgd?file=%2Fsrc%2Fmain.rs%3A1%2C1-69%2C1&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/12-transition-0-7-ln2hgd?file=%2Fsrc%2Fmain.rs%3A1%2C1-69%2C1&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use gloo_timers::future::TimeoutFuture;
use leptos::prelude::*;

async fn important_api_call(id: usize) -> String {
    TimeoutFuture::new(1_000).await;
    match id {
        0 => "Alice",
        1 => "Bob",
        2 => "Carol",
        _ => "User not found",
    }
    .to_string()
}

#[component]
fn App() -> impl IntoView {
    let (tab, set_tab) = signal(0);
    let (pending, set_pending) = signal(false);

    // this will reload every time `tab` changes
    let user_data = LocalResource::new(move || important_api_call(tab.get()));

    view! {
        <div class="buttons">
            <button
                on:click=move |_| set_tab.set(0)
                class:selected=move || tab.get() == 0
            >
                "Tab A"
            </button>
            <button
                on:click=move |_| set_tab.set(1)
                class:selected=move || tab.get() == 1
            >
                "Tab B"
            </button>
            <button
                on:click=move |_| set_tab.set(2)
                class:selected=move || tab.get() == 2
            >
                "Tab C"
            </button>
        </div>
        <p>
            {move || if pending.get() {
                "Hang on..."
            } else {
                "Ready."
            }}
        </p>
        <Transition
            // the fallback will show initially
            // on subsequent reloads, the current child will
            // continue showing
            fallback=move || view! { <p>"Loading initial data..."</p> }
            // this will be set to `true` whenever the transition is ongoing
            set_pending
        >
            <p>
                {move || user_data.read().as_deref().map(ToString::to_string)}
            </p>
        </Transition>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
