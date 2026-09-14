# การส่ง children ให้คอมโพเนนต์

เป็นเรื่องปกติอย่างยิ่งที่คุณจะต้องการส่งคอมโพเนนต์ลูก (children) เข้าไปในคอมโพเนนต์อื่น เช่นเดียวกับที่คุณสามารถใส่เอลิเมนต์ลูกเข้าไปในเอลิเมนต์ HTML ได้ ตัวอย่างเช่น สมมติว่าเรามีคอมโพเนนต์ `<FancyForm/>` ที่สร้างขึ้นเพื่อเสริมความสามารถให้กับ `<form>` ของ HTML เราย่อมต้องการวิธีส่งอินพุตและปุ่มต่าง ๆ เข้าไปข้างใน:

```rust
view! {
    <FancyForm>
        <fieldset>
            <label>
                "Some Input"
                <input type="text" name="something"/>
            </label>
        </fieldset>
        <button>"Submit"</button>
    </FancyForm>
}
```

เราจะทำสิ่งนี้ใน Leptos ได้อย่างไร? โดยหลักการพื้นฐานแล้ว มี 2 วิธีในการส่งคอมโพเนนต์หนึ่งไปยังอีกคอมโพเนนต์หนึ่ง:

1. **render props**: พร็อพที่เป็นฟังก์ชัน ซึ่งเมื่อเรียกใช้จะคืนค่าออกมาเป็นวิว (view)
2. พร็อพ **`children`**: พร็อพพิเศษของคอมโพเนนต์ที่รวบรวมเนื้อหาทั้งหมดที่คุณส่งเข้ามาเป็นคอมโพเนนต์ลูกไว้

ในความเป็นจริง คุณเคยเห็นการใช้งานทั้งสองรูปแบบนี้ร่วมกันมาแล้วในคอมโพเนนต์ [`<Show/>`](06_control_flow.md#show):

```rust
view! {
  <Show
    // `when` is a normal prop
    when=move || value.get() > 5
    // `fallback` is a "render prop": a function that returns a view
    fallback=|| view! { <Small/> }
  >
    // `<Big/>` (and anything else here)
    // will be given to the `children` prop
    <Big/>
  </Show>
}
```

เรามาลองเขียนคอมโพเนนต์ที่รับทั้ง `children` และ render prop กัน:

```rust
/// Displays a `render_prop` and some children within markup.
#[component]
pub fn TakesChildren<F, IV>(
    /// Takes a function (type F) that returns anything that can be
    /// converted into a View (type IV)
    render_prop: F,
    /// `children` can take one of several different types, each of which
    /// is a function that returns some view type
    children: Children,
) -> impl IntoView
where
    F: Fn() -> IV,
    IV: IntoView,
{
    view! {
        <h1><code>"<TakesChildren/>"</code></h1>
        <h2>"Render Prop"</h2>
        {render_prop()}
        <hr/>
        <h2>"Children"</h2>
        {children()}
    }
}
```

`render_prop` และ `children` ต่างก็เป็นฟังก์ชัน ดังนั้นเราจึงสามารถเรียกใช้พวกมันเพื่อสร้างวิวที่ต้องการออกมาได้ โดยเฉพาะอย่างยิ่ง `Children` นั้นเป็น type alias ของ `Box<dyn FnOnce() -> AnyView>` (ดีใจใช่ไหมล่ะที่เราตั้งชื่อมันว่า `Children` แทน!) ซึ่ง `AnyView` ที่คืนค่าออกมานั้นเป็นวิวแบบ opaque ที่ถูกลบข้อมูลชนิด (type-erased) ออกไป ทำให้คุณไม่สามารถตรวจสอบโครงสร้างภายในของมันได้ แต่ยังมีชนิดของลูกแบบอื่น ๆ ให้เลือกใช้ ตัวอย่างเช่น `ChildrenFragment` ซึ่งจะคืนค่าออกมาเป็น `Fragment` อันเป็นคอลเลกชันที่คุณสามารถนำมาวนลูป (iterate) เข้าถึงโหนดลูกแต่ละตัวข้างในได้

> หากคุณต้องการ `Fn` หรือ `FnMut` เพราะจำเป็นต้องเรียกใช้ `children` มากกว่าหนึ่งครั้ง Leptos ก็มี type alias อย่าง `ChildrenFn` และ `ChildrenMut` ให้เลือกใช้ด้วยเช่นกัน

เราสามารถนำคอมโพเนนต์นี้ไปใช้งานได้ดังนี้:

```rust
view! {
    <TakesChildren render_prop=|| view! { <p>"Hi, there!"</p> }>
        // these get passed to `children`
        "Some text"
        <span>"A span"</span>
    </TakesChildren>
}
```

## children ที่มีชนิด: สล็อต

จนถึงตอนนี้ เราได้พูดถึงคอมโพเนนต์ที่มีพร็อพ `children` เพียงตัวเดียว แต่ในบางครั้ง การสร้างคอมโพเนนต์ที่คาดหวัง children หลายประเภทซึ่งมีชนิดข้อมูลต่างกันก็มีประโยชน์อย่างยิ่ง ตัวอย่างเช่น:
```rust
view! {
    <If condition=a_is_true>
        <Then>"Show content when a is true"</Then>
        <ElseIf condition=b_is_true>"b is true"</ElseIf>
        <ElseIf condition=c_is_true>"c is true"</ElseIf>
        <Else>"None of the above are true"</Else>
    </If>
}
```
คอมโพเนนต์ `If` คาดหวัง child ที่เป็น `Then` เสมอ โดยอาจมี `ElseIf` หลายตัวหรือไม่มีเลยก็ได้ รวมถึงมี `Else` เสริมได้อีกหนึ่งตัว เพื่อรองรับรูปแบบนี้ Leptos จึงเตรียมฟีเจอร์[สล็อต (slots)](https://docs.rs/leptos/latest/leptos/attr.slot.html) ไว้ให้ใช้งาน

แอตทริบิวต์มาโคร `#[slot]` ใช้สำหรับกำกับ struct ของ Rust ทั่วไปเพื่อกำหนดให้เป็นสล็อตของคอมโพเนนต์:
```rust
// A simple struct annotated with `#[slot]`,
// which expects children
#[slot]
struct Then {
    children: ChildrenFn,
}
```

สล็อตนี้สามารถนำมาใช้เป็นพร็อพในคอมโพเนนต์ได้:
```rust
#[component]
fn If(
    condition: Signal<bool>,
    // Component slot, should be passed through the <Then slot> syntax
    then_slot: Then,
) -> impl IntoView {
    move || {
        if condition.get() {
            (then_slot.children)().into_any()
        } else {
            ().into_any()
        }
    }
}
```

ในตอนนี้ คอมโพเนนต์ `If` คาดหวัง child ที่มีชนิดเป็น `Then` คุณจะต้องระบุชื่อสล็อตที่จะส่งผ่านไวยากรณ์ `slot:<prop_name>`:
```rust
view! {
    <If condition=a_is_true>
        // The `If` component always expects a `Then` child for `then_slot`
        <Then slot:then_slot>"Show content when a is true"</Then>
    </If>
}
```

> หากคุณระบุ `slot` โดยไม่ใส่ชื่อ สล็อตที่เลือกจะใช้ชื่อเริ่มต้นเป็นชื่อของ struct ในรูปแบบ snake_case ดังนั้นในกรณีนี้ `<Then slot>` จึงมีค่าเท่ากับ `<Then slot:then>` ทุกประการ

คุณสามารถดูตัวอย่างการใช้งานฉบับสมบูรณ์ได้ที่ [ตัวอย่างสล็อต](https://github.com/leptos-rs/leptos/tree/main/examples/slots)

### ตัวจัดการเหตุการณ์บนสล็อต

ตัวจัดการเหตุการณ์ (event handler) ไม่สามารถระบุลงบนแท็กสล็อตได้โดยตรง เช่น:
```rust
<ComponentWithSlot>
    // ⚠️ Event handler `on:click` directly on slot is not allowed
    <SlotWithChildren slot:slot on:click=move |_| {}> 
        <h1>"Hello, World!"</h1>
    </SlotWithChildren>
</ComponentWithSlot>
```

วิธีที่ถูกต้องคือ ให้ห่อเนื้อหาภายในของสล็อตด้วยเอลิเมนต์ HTML ปกติ แล้วค่อยติดตัวจัดการเหตุการณ์ไว้ที่เอลิเมนต์นั้นแทน:
```rust
<ComponentWithSlot>
    <SlotWithChildren slot:slot>
        // ✅ Event handler is not defined directly on slot
        <div on:click=move |_| {}>
            <h1>"Hello, World!"</h1>
        </div>
    </SlotWithChildren>
</ComponentWithSlot>
```

## การจัดการ children

ชนิดข้อมูล [`Fragment`](https://docs.rs/leptos/latest/leptos/tachys/view/fragment/struct.Fragment.html) โดยพื้นฐานแล้วคือตัวห่อหุ้ม `Vec<AnyView>` ซึ่งคุณสามารถแทรกมันลงไปในตำแหน่งใดก็ได้ภายในวิวของคุณ

แต่คุณยังสามารถเข้าถึงวิวข้างในเหล่านั้นได้โดยตรงเพื่อนำมาจัดการหรือปรับแต่งต่อได้ ตัวอย่างเช่น นี่คือคอมโพเนนต์ที่รับ children เข้ามา แล้วนำแต่ละตัวมาห่อหุ้มใหม่เพื่อเรนเดอร์เป็นรายการแบบไม่มีลำดับ (unordered list):

```rust
/// Wraps each child in an `<li>` and embeds them in a `<ul>`.
#[component]
pub fn WrapsChildren(children: ChildrenFragment) -> impl IntoView {
    // children() returns a `Fragment`, which has a
    // `nodes` field that contains a Vec<View>
    // this means we can iterate over the children
    // to create something new!
    let children = children()
        .nodes
        .into_iter()
        .map(|child| view! { <li>{child}</li> })
        .collect::<Vec<_>>();

    view! {
        <h1><code>"<WrapsChildren/>"</code></h1>
        // wrap our wrapped children in a UL
        <ul>{children}</ul>
    }
}
```

เมื่อนำไปเรียกใช้ คอมโพเนนต์นี้จะสร้างลิสต์รายการขึ้นมา:

```rust
view! {
    <WrapsChildren>
        "A"
        "B"
        "C"
    </WrapsChildren>
}
```

```admonish sandbox title="ตัวอย่างสด" collapsible=true

[คลิกเพื่อเปิด CodeSandbox](https://codesandbox.io/p/devbox/9-component-children-0-7-736s9r?file=%2Fsrc%2Fmain.rs%3A1%2C1-90%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb)

<noscript>
  โปรดเปิดใช้งาน JavaScript เพื่อดูตัวอย่าง
</noscript>

<template>
  <iframe src="https://codesandbox.io/p/devbox/9-component-children-0-7-736s9r?file=%2Fsrc%2Fmain.rs%3A1%2C1-90%2C2&workspaceId=478437f3-1f86-4b1e-b665-5c27a31451fb" width="100%" height="1000px" style="max-height: 100vh"></iframe>
</template>

```

<details>
<summary>ซอร์สโค้ด CodeSandbox</summary>

```rust
use leptos::prelude::*;

// Often, you want to pass some kind of child view to another
// component. There are two basic patterns for doing this:
// - "render props": creating a component prop that takes a function
//   that creates a view
// - the `children` prop: a special property that contains content
//   passed as the children of a component in your view, not as a
//   property

#[component]
pub fn App() -> impl IntoView {
    let (items, set_items) = signal(vec![0, 1, 2]);
    let render_prop = move || {
        let len = move || items.read().len();
        view! {
            <p>"Length: " {len}</p>
        }
    };

    view! {
        // This component just displays the two kinds of children,
        // embedding them in some other markup
        <TakesChildren
            // for component props, you can shorthand
            // `render_prop=render_prop` => `render_prop`
            // (this doesn't work for HTML element attributes)
            render_prop
        >
            // these look just like the children of an HTML element
            <p>"Here's a child."</p>
            <p>"Here's another child."</p>
        </TakesChildren>
        <hr/>
        // This component actually iterates over and wraps the children
        <WrapsChildren>
            <p>"Here's a child."</p>
            <p>"Here's another child."</p>
        </WrapsChildren>
    }
}

/// Displays a `render_prop` and some children within markup.
#[component]
pub fn TakesChildren<F, IV>(
    /// Takes a function (type F) that returns anything that can be
    /// converted into a View (type IV)
    render_prop: F,
    /// `children` takes the `Children` type
    /// this is an alias for `Box<dyn FnOnce() -> Fragment>`
    /// ... aren't you glad we named it `Children` instead?
    children: Children,
) -> impl IntoView
where
    F: Fn() -> IV,
    IV: IntoView,
{
    view! {
        <h1><code>"<TakesChildren/>"</code></h1>
        <h2>"Render Prop"</h2>
        {render_prop()}
        <hr/>
        <h2>"Children"</h2>
        {children()}
    }
}

/// Wraps each child in an `<li>` and embeds them in a `<ul>`.
#[component]
pub fn WrapsChildren(children: ChildrenFragment) -> impl IntoView {
    // children() returns a `Fragment`, which has a
    // `nodes` field that contains a Vec<View>
    // this means we can iterate over the children
    // to create something new!
    let children = children()
        .nodes
        .into_iter()
        .map(|child| view! { <li>{child}</li> })
        .collect::<Vec<_>>();

    view! {
        <h1><code>"<WrapsChildren/>"</code></h1>
        // wrap our wrapped children in a UL
        <ul>{children}</ul>
    }
}

fn main() {
    leptos::mount::mount_to_body(App)
}
```

</details>
</preview>
